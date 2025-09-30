"""
Podcast generator service that integrates YouTube video processing with n8n RAG workflow.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from youtube_chat_cli.core.youtube_api import get_youtube_client, YouTubeVideo
from youtube_chat_cli.services.transcription.processor import get_source_processor
from youtube_chat_cli.services.tts.service import get_tts_service
from youtube_chat_cli.services.n8n.client import get_n8n_client
from youtube_chat_cli.core.database import get_video_database
from youtube_chat_cli.utils.session_manager import SessionManager
from youtube_chat_cli.services.content.source_manager import get_source_manager, SourceFilter
from youtube_chat_cli.services.podcast.styles import get_style_manager, PodcastStyle, PodcastLength, PodcastTone

logger = logging.getLogger(__name__)


class PodcastGenerator:
    """Service for generating podcasts from YouTube videos with n8n RAG integration."""
    
    def __init__(self):
        """Initialize the podcast generator."""
        self.youtube_client = get_youtube_client()
        self.source_processor = get_source_processor()
        self.tts_service = get_tts_service()
        self.n8n_client = get_n8n_client()
        self.video_db = get_video_database()
        self.source_manager = get_source_manager()
        self.style_manager = get_style_manager()

        # Create output directory
        self.output_dir = Path.home() / ".youtube-chat-cli" / "podcasts"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_podcast_from_video(self, video_url: str, 
                                  podcast_style: str = "summary",
                                  voice: str = "en-US-AriaNeural",
                                  use_rag: bool = True,
                                  session_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate a podcast from a YouTube video.
        
        Args:
            video_url: YouTube video URL
            podcast_style: Style of podcast ('summary', 'detailed', 'qa', 'analysis')
            voice: TTS voice to use
            use_rag: Whether to use n8n RAG for enhanced content generation
            session_id: Session ID for RAG context
            
        Returns:
            Dictionary with podcast generation results
        """
        logger.info(f"Starting podcast generation for: {video_url}")
        
        try:
            # Step 1: Extract video information and transcript
            video_data = self._extract_video_data(video_url)
            
            # Step 2: Process content through n8n RAG if enabled
            if use_rag:
                enhanced_content = self._enhance_with_rag(video_data, podcast_style, session_id)
            else:
                enhanced_content = self._generate_local_content(video_data, podcast_style)
            
            # Step 3: Generate podcast script
            podcast_script = self._create_podcast_script(video_data, enhanced_content, podcast_style)
            
            # Step 4: Generate audio
            audio_file = self._generate_audio(podcast_script, voice, video_data['video_id'])
            
            # Step 5: Save metadata
            metadata = self._save_podcast_metadata(video_data, podcast_script, audio_file, podcast_style)
            
            logger.info(f"Podcast generated successfully: {audio_file}")
            
            return {
                "status": "success",
                "video_data": video_data,
                "audio_file": str(audio_file),
                "script": podcast_script,
                "metadata": metadata,
                "enhanced_with_rag": use_rag
            }
            
        except Exception as e:
            logger.error(f"Failed to generate podcast: {e}")
            return {
                "status": "error",
                "error": str(e),
                "video_url": video_url
            }
    
    def _extract_video_data(self, video_url: str) -> Dict[str, Any]:
        """Extract video data and transcript."""
        logger.info("Extracting video data and transcript...")
        
        # Get video metadata
        video_id = self.youtube_client.extract_video_id(video_url)
        if not video_id:
            raise ValueError(f"Invalid YouTube URL: {video_url}")
        
        videos = self.youtube_client.get_video_details([video_id])
        if not videos:
            raise ValueError(f"Video not found: {video_id}")
        
        video = videos[0]
        
        # Process transcript
        processed_content = self.source_processor.process_source(video_url)
        
        return {
            "video_id": video_id,
            "title": video.title,
            "description": video.description,
            "channel": video.channel_title,
            "duration": video.duration_seconds,
            "view_count": video.view_count,
            "published_at": video.published_at,
            "url": video_url,
            "transcript": processed_content.get("text", ""),
            "summary": processed_content.get("summary", ""),
            "key_points": processed_content.get("key_points", [])
        }
    
    def _enhance_with_rag(self, video_data: Dict[str, Any], 
                         podcast_style: str, 
                         session_id: Optional[str] = None) -> Dict[str, Any]:
        """Enhance content using n8n RAG workflow."""
        logger.info("Enhancing content with n8n RAG workflow...")
        
        if not session_id:
            session_id = f"podcast_{video_data['video_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Send video data to n8n for processing
        try:
            self.n8n_client.send_video_data(video_data)
        except Exception as e:
            logger.warning(f"Failed to send video data to n8n: {e}")
        
        # Generate podcast content based on style
        prompts = self._get_podcast_prompts(podcast_style, video_data)
        
        enhanced_content = {}
        for section, prompt in prompts.items():
            try:
                response = self.n8n_client.send_chat_message(prompt, session_id)
                enhanced_content[section] = response
                logger.debug(f"Generated {section} content via RAG")
            except Exception as e:
                logger.warning(f"RAG enhancement failed for {section}: {e}")
                enhanced_content[section] = self._generate_fallback_content(section, video_data)
        
        return enhanced_content
    
    def _generate_local_content(self, video_data: Dict[str, Any], podcast_style: str) -> Dict[str, Any]:
        """Generate content locally without RAG."""
        logger.info("Generating content locally...")
        
        content = {
            "introduction": f"Welcome to today's podcast. We're discussing '{video_data['title']}' from {video_data['channel']}.",
            "main_content": video_data.get("summary", video_data["transcript"][:2000]),
            "key_insights": "\n".join([f"• {point}" for point in video_data.get("key_points", [])[:5]]),
            "conclusion": "Thank you for listening. This content was generated from the YouTube video analysis."
        }
        
        return content
    
    def _get_podcast_prompts(self, style: str, video_data: Dict[str, Any]) -> Dict[str, str]:
        """Get prompts for different podcast styles."""
        base_context = f"""
        Video Title: {video_data['title']}
        Channel: {video_data['channel']}
        Duration: {video_data.get('duration', 'Unknown')} seconds
        
        Based on this YouTube video content, please generate:
        """
        
        if style == "summary":
            return {
                "introduction": f"{base_context} A brief, engaging introduction for a podcast summary.",
                "main_content": f"{base_context} A comprehensive but concise summary of the main points and key insights.",
                "conclusion": f"{base_context} A thoughtful conclusion that ties everything together."
            }
        elif style == "detailed":
            return {
                "introduction": f"{base_context} A detailed introduction setting up the topic and context.",
                "main_content": f"{base_context} An in-depth analysis covering all major points, examples, and implications.",
                "key_insights": f"{base_context} The most important takeaways and actionable insights.",
                "conclusion": f"{base_context} A comprehensive conclusion with next steps or further considerations."
            }
        elif style == "qa":
            return {
                "introduction": f"{base_context} An introduction framing this as a Q&A exploration of the topic.",
                "main_content": f"{base_context} Key questions and answers that would help someone understand this topic deeply.",
                "conclusion": f"{base_context} A conclusion summarizing the key questions and answers covered."
            }
        elif style == "analysis":
            return {
                "introduction": f"{base_context} An analytical introduction examining the significance of this content.",
                "main_content": f"{base_context} A critical analysis of the arguments, evidence, and implications presented.",
                "expert_perspective": f"{base_context} Expert-level insights and connections to broader trends or concepts.",
                "conclusion": f"{base_context} An analytical conclusion with implications and future considerations."
            }
        else:
            return self._get_podcast_prompts("summary", video_data)
    
    def _generate_fallback_content(self, section: str, video_data: Dict[str, Any]) -> str:
        """Generate fallback content when RAG fails."""
        fallbacks = {
            "introduction": f"Today we're exploring '{video_data['title']}' from {video_data['channel']}. This video provides valuable insights that we'll break down for you.",
            "main_content": video_data.get("summary", video_data["transcript"][:1500]),
            "key_insights": "This content offers several important takeaways that are worth considering.",
            "conclusion": "Thank you for listening to this analysis. The original content provides much more detail.",
            "expert_perspective": "From an analytical perspective, this content contributes to our understanding of the topic."
        }
        return fallbacks.get(section, "Content not available.")
    
    def _create_podcast_script(self, video_data: Dict[str, Any], 
                              enhanced_content: Dict[str, Any], 
                              style: str) -> str:
        """Create the final podcast script."""
        logger.info("Creating podcast script...")
        
        script_parts = []
        
        # Introduction
        if "introduction" in enhanced_content:
            script_parts.append(enhanced_content["introduction"])
        
        # Main content
        if "main_content" in enhanced_content:
            script_parts.append("\n\n" + enhanced_content["main_content"])
        
        # Additional sections based on style
        for section in ["key_insights", "expert_perspective"]:
            if section in enhanced_content:
                script_parts.append("\n\n" + enhanced_content[section])
        
        # Conclusion
        if "conclusion" in enhanced_content:
            script_parts.append("\n\n" + enhanced_content["conclusion"])
        
        # Add source attribution
        script_parts.append(f"\n\nThis podcast was generated from the YouTube video '{video_data['title']}' by {video_data['channel']}. You can find the original video at {video_data['url']}")
        
        return "".join(script_parts)
    
    def _generate_audio(self, script: str, voice: str, video_id: str) -> Path:
        """Generate audio from the script."""
        logger.info("Generating audio from script...")
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"podcast_{video_id}_{timestamp}.wav"
        output_file = self.output_dir / filename
        
        # Generate audio
        self.tts_service.generate_audio(
            text=script,
            output_file=str(output_file),
            voice=voice
        )
        
        return output_file
    
    def _save_podcast_metadata(self, video_data: Dict[str, Any], 
                              script: str, 
                              audio_file: Path, 
                              style: str) -> Dict[str, Any]:
        """Save podcast metadata."""
        metadata = {
            "video_id": video_data["video_id"],
            "video_title": video_data["title"],
            "video_channel": video_data["channel"],
            "video_url": video_data["url"],
            "podcast_style": style,
            "audio_file": str(audio_file),
            "script_length": len(script),
            "generated_at": datetime.now().isoformat(),
            "script": script
        }
        
        # Save to JSON file
        metadata_file = audio_file.with_suffix('.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return metadata
    
    def list_generated_podcasts(self) -> List[Dict[str, Any]]:
        """List all generated podcasts."""
        podcasts = []
        
        for json_file in self.output_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    podcasts.append(metadata)
            except Exception as e:
                logger.warning(f"Failed to read metadata from {json_file}: {e}")
        
        # Sort by generation time (newest first)
        podcasts.sort(key=lambda x: x.get("generated_at", ""), reverse=True)
        return podcasts

    def generate_multi_source_podcast(self,
                                    source_filter: SourceFilter,
                                    podcast_style: str = "summary",
                                    podcast_length: str = "medium",
                                    podcast_tone: str = "professional",
                                    chunk_duration: int = 600,  # 10 minutes
                                    voice: str = "en-US-AriaNeural",
                                    use_rag: bool = True,
                                    session_id: Optional[str] = None,
                                    title: Optional[str] = None) -> Dict[str, Any]:
        """Generate a podcast from multiple sources.

        Args:
            source_filter: Filter for selecting sources
            podcast_style: Style of podcast
            podcast_length: Length category (short, medium, long, extended)
            podcast_tone: Tone of the podcast
            chunk_duration: Duration of each chunk in seconds
            voice: TTS voice to use
            use_rag: Whether to use n8n RAG for enhanced content generation
            session_id: Session ID for RAG context
            title: Custom title for the podcast

        Returns:
            Dictionary with podcast generation results
        """
        logger.info("Starting multi-source podcast generation")

        try:
            # Step 1: Get sources matching filter
            sources = self.source_manager.get_sources(source_filter)
            if not sources:
                raise ValueError("No sources found matching the filter criteria")

            logger.info(f"Found {len(sources)} sources for podcast generation")

            # Step 2: Process all sources
            processed_content = []
            for source in sources:
                content = self.source_manager.process_source(source.source_id)
                if content:
                    processed_content.append(content)

            if not processed_content:
                raise ValueError("No content could be processed from sources")

            # Step 3: Generate enhanced content using RAG or local processing
            if use_rag:
                enhanced_content = self._enhance_multi_source_with_rag(
                    processed_content, podcast_style, podcast_tone, session_id
                )
            else:
                enhanced_content = self._generate_multi_source_local_content(
                    processed_content, podcast_style, podcast_tone
                )

            # Step 4: Create podcast script
            podcast_script = self._create_multi_source_podcast_script(
                processed_content, enhanced_content, podcast_style, podcast_tone, title
            )

            # Step 5: Handle chunking if needed
            style_enum = PodcastStyle(podcast_style)
            length_enum = PodcastLength(podcast_length)
            target_duration = self.style_manager.get_estimated_duration(style_enum, length_enum)

            if target_duration > chunk_duration:
                chunks = self._create_podcast_chunks(podcast_script, chunk_duration, target_duration)
                audio_files = []

                for i, chunk in enumerate(chunks):
                    chunk_file = self._generate_audio(
                        chunk, voice, f"multi_source_chunk_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    )
                    audio_files.append(chunk_file)

                # Merge chunks into final audio
                final_audio = self._merge_audio_chunks(audio_files)
            else:
                final_audio = self._generate_audio(
                    podcast_script, voice, f"multi_source_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )

            # Step 6: Save metadata
            metadata = self._save_multi_source_podcast_metadata(
                processed_content, podcast_script, final_audio, podcast_style,
                podcast_length, podcast_tone, title
            )

            logger.info(f"Multi-source podcast generated successfully: {final_audio}")

            return {
                "status": "success",
                "sources_processed": len(processed_content),
                "audio_file": str(final_audio),
                "script": podcast_script,
                "metadata": metadata,
                "enhanced_with_rag": use_rag,
                "style": podcast_style,
                "length": podcast_length,
                "tone": podcast_tone
            }

        except Exception as e:
            logger.error(f"Failed to generate multi-source podcast: {e}")
            return {
                "status": "error",
                "error": str(e),
                "sources_attempted": len(source_filter.file_types) if source_filter.file_types else 0
            }

    def _enhance_multi_source_with_rag(self,
                                      content: List[Any],
                                      style: str,
                                      tone: str,
                                      session_id: Optional[str] = None) -> Dict[str, Any]:
        """Enhance multi-source content using n8n RAG workflow."""
        logger.info("Enhancing multi-source content with n8n RAG workflow...")

        if not session_id:
            session_id = f"multi_podcast_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Send content summary to n8n
        try:
            content_summary = self._create_multi_source_summary(content)
            self.n8n_client.send_chat_message(
                f"I'm creating a {style} podcast with {tone} tone from {len(content)} sources. "
                f"Content summary: {content_summary}",
                session_id
            )
        except Exception as e:
            logger.warning(f"Failed to send content to n8n: {e}")

        # Generate enhanced content sections
        prompts = self._get_multi_source_podcast_prompts(style, tone, content)

        enhanced_content = {}
        for section, prompt in prompts.items():
            try:
                response = self.n8n_client.send_chat_message(prompt, session_id)
                enhanced_content[section] = response.get('response', '')
                logger.debug(f"Generated {section} content via RAG")
            except Exception as e:
                logger.warning(f"RAG enhancement failed for {section}: {e}")
                enhanced_content[section] = self._generate_fallback_multi_source_content(section, content)

        return enhanced_content

    def _generate_multi_source_local_content(self,
                                           content: List[Any],
                                           style: str,
                                           tone: str) -> Dict[str, Any]:
        """Generate multi-source content locally without RAG."""
        logger.info("Generating multi-source content locally...")

        # Combine all content
        all_text = "\n\n".join([c.text_content[:1000] for c in content])
        all_summaries = [c.summary for c in content if c.summary]
        all_key_points = []
        for c in content:
            all_key_points.extend(c.key_points[:3])

        content_dict = {
            "introduction": f"Welcome to this {style} podcast covering insights from {len(content)} sources.",
            "main_content": " ".join(all_summaries[:5]) if all_summaries else all_text[:2000],
            "key_insights": "\n".join([f"• {point}" for point in all_key_points[:10]]),
            "conclusion": f"Thank you for listening to this comprehensive analysis of {len(content)} sources."
        }

        return content_dict

    def _create_multi_source_summary(self, content: List[Any]) -> str:
        """Create a summary of all content for RAG processing."""
        summary_parts = []
        for i, c in enumerate(content[:10]):  # Limit to first 10 for summary
            summary_parts.append(f"Source {i+1}: {c.summary or c.text_content[:200]}...")
        return "\n".join(summary_parts)

    def _get_multi_source_podcast_prompts(self, style: str, tone: str, content: List[Any]) -> Dict[str, str]:
        """Get prompts for multi-source podcast generation."""
        content_summary = self._create_multi_source_summary(content)

        base_context = f"""
        Create a {style} podcast with {tone} tone based on {len(content)} sources.

        Content summary:
        {content_summary}

        Generate:
        """

        return {
            "introduction": f"{base_context} An engaging introduction that sets up the multi-source analysis.",
            "main_content": f"{base_context} The main content synthesizing insights from all sources.",
            "key_insights": f"{base_context} The most important takeaways and patterns across sources.",
            "conclusion": f"{base_context} A comprehensive conclusion tying everything together."
        }

    def _create_multi_source_podcast_script(self,
                                          content: List[Any],
                                          enhanced_content: Dict[str, Any],
                                          style: str,
                                          tone: str,
                                          title: Optional[str] = None) -> str:
        """Create the final multi-source podcast script."""
        logger.info("Creating multi-source podcast script...")

        script_title = title or f"Multi-Source {style.title()} Podcast"

        script_parts = [f"# {script_title}\n"]

        # Introduction
        if "introduction" in enhanced_content:
            script_parts.append(enhanced_content["introduction"])

        # Main content
        if "main_content" in enhanced_content:
            script_parts.append("\n\n" + enhanced_content["main_content"])

        # Key insights
        if "key_insights" in enhanced_content:
            script_parts.append("\n\n## Key Insights\n" + enhanced_content["key_insights"])

        # Conclusion
        if "conclusion" in enhanced_content:
            script_parts.append("\n\n" + enhanced_content["conclusion"])

        # Add source attribution
        script_parts.append(f"\n\nThis podcast was generated from {len(content)} sources including documents, videos, and other content.")

        return "".join(script_parts)

    def _create_podcast_chunks(self, script: str, chunk_duration: int, total_duration: int) -> List[str]:
        """Split podcast script into chunks based on duration."""
        # Estimate words per minute (average speaking rate: 150-160 WPM)
        words_per_minute = 155
        words_per_second = words_per_minute / 60

        total_words = len(script.split())
        chunk_words = int(chunk_duration * words_per_second)

        words = script.split()
        chunks = []

        for i in range(0, len(words), chunk_words):
            chunk_words_list = words[i:i + chunk_words]
            chunk_text = " ".join(chunk_words_list)

            # Add smooth transitions
            if i > 0:
                chunk_text = "Continuing our discussion... " + chunk_text
            if i + chunk_words < len(words):
                chunk_text += " We'll continue with more insights in just a moment."

            chunks.append(chunk_text)

        return chunks

    def _merge_audio_chunks(self, audio_files: List[Path]) -> Path:
        """Merge multiple audio chunks into a single file."""
        # Placeholder implementation - would use audio processing library
        logger.info(f"Merging {len(audio_files)} audio chunks")

        # For now, just return the first file
        # In a real implementation, would use pydub or similar to concatenate
        merged_file = self.output_dir / f"merged_podcast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

        # Copy first file as placeholder
        import shutil
        shutil.copy2(audio_files[0], merged_file)

        return merged_file

    def _save_multi_source_podcast_metadata(self,
                                          content: List[Any],
                                          script: str,
                                          audio_file: Path,
                                          style: str,
                                          length: str,
                                          tone: str,
                                          title: Optional[str] = None) -> Dict[str, Any]:
        """Save multi-source podcast metadata."""
        metadata = {
            "title": title or f"Multi-Source {style.title()} Podcast",
            "style": style,
            "length": length,
            "tone": tone,
            "sources_count": len(content),
            "source_types": list(set([c.content_type for c in content])),
            "audio_file": str(audio_file),
            "script_length": len(script),
            "word_count": len(script.split()),
            "generated_at": datetime.now().isoformat(),
            "script": script,
            "sources": [
                {
                    "source_id": c.source_id,
                    "content_type": c.content_type,
                    "word_count": c.word_count
                } for c in content
            ]
        }

        # Save to JSON file
        metadata_file = audio_file.with_suffix('.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return metadata

    def _generate_fallback_multi_source_content(self, section: str, content: List[Any]) -> str:
        """Generate fallback content for multi-source when RAG fails."""
        fallbacks = {
            "introduction": f"Welcome to this comprehensive analysis of {len(content)} sources.",
            "main_content": f"This podcast synthesizes insights from {len(content)} different sources.",
            "key_insights": "Key insights and patterns have been identified across all sources.",
            "conclusion": "Thank you for listening to this multi-source analysis."
        }
        return fallbacks.get(section, "Content not available.")


# Global podcast generator instance
_podcast_generator = None

def get_podcast_generator() -> PodcastGenerator:
    """Get or create the global podcast generator instance."""
    global _podcast_generator
    if _podcast_generator is None:
        _podcast_generator = PodcastGenerator()
    return _podcast_generator
