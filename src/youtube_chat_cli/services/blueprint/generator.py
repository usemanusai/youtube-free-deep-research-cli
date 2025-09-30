"""
Blueprint generation service for creating comprehensive documentation from multiple sources.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import hashlib

from youtube_chat_cli.services.content.source_manager import (
    get_source_manager, SourceFilter, SourceType, SourceLocation, ProcessedContent
)
from youtube_chat_cli.services.n8n.client import get_n8n_client
from youtube_chat_cli.utils.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class BlueprintFormat(Enum):
    """Supported blueprint output formats."""
    MARKDOWN = "markdown"
    PDF = "pdf"
    HTML = "html"
    DOCX = "docx"
    JSON = "json"


class BlueprintStyle(Enum):
    """Blueprint generation styles."""
    COMPREHENSIVE = "comprehensive"  # Full detailed documentation
    EXECUTIVE = "executive"          # High-level summary
    TECHNICAL = "technical"          # Technical deep-dive
    EDUCATIONAL = "educational"      # Learning-focused
    REFERENCE = "reference"          # Quick reference guide


@dataclass
class BlueprintSection:
    """A section in the blueprint."""
    title: str
    content: str
    subsections: List['BlueprintSection']
    metadata: Dict[str, Any]
    sources: List[str]  # Source IDs that contributed to this section


@dataclass
class BlueprintConfig:
    """Configuration for blueprint generation."""
    title: str
    style: BlueprintStyle
    format: BlueprintFormat
    include_toc: bool = True
    include_sources: bool = True
    include_metadata: bool = True
    max_content_length: Optional[int] = None
    sections: List[str] = None  # Custom section order
    template_path: Optional[str] = None


class BlueprintGenerator:
    """Service for generating comprehensive documentation blueprints."""
    
    def __init__(self):
        """Initialize the blueprint generator."""
        self.source_manager = get_source_manager()
        self.n8n_client = get_n8n_client()
        self.llm_service = get_llm_service()
        
        # Create output directory
        self.output_dir = Path.home() / ".youtube-chat-cli" / "blueprints"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize templates
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[BlueprintStyle, str]:
        """Load blueprint templates for different styles."""
        return {
            BlueprintStyle.COMPREHENSIVE: """
# {title}

## Table of Contents
{toc}

## Executive Summary
{executive_summary}

## Overview
{overview}

## Key Findings
{key_findings}

## Detailed Analysis
{detailed_analysis}

## Recommendations
{recommendations}

## Conclusion
{conclusion}

## Sources
{sources}

## Appendices
{appendices}
""",
            BlueprintStyle.EXECUTIVE: """
# {title}

## Executive Summary
{executive_summary}

## Key Points
{key_points}

## Strategic Implications
{strategic_implications}

## Next Steps
{next_steps}

## Sources
{sources}
""",
            BlueprintStyle.TECHNICAL: """
# {title}

## Technical Overview
{technical_overview}

## Architecture
{architecture}

## Implementation Details
{implementation_details}

## Performance Analysis
{performance_analysis}

## Best Practices
{best_practices}

## Troubleshooting
{troubleshooting}

## References
{references}
""",
            BlueprintStyle.EDUCATIONAL: """
# {title}

## Learning Objectives
{learning_objectives}

## Prerequisites
{prerequisites}

## Core Concepts
{core_concepts}

## Step-by-Step Guide
{step_by_step_guide}

## Examples
{examples}

## Practice Exercises
{practice_exercises}

## Additional Resources
{additional_resources}
""",
            BlueprintStyle.REFERENCE: """
# {title}

## Quick Reference
{quick_reference}

## Commands/APIs
{commands_apis}

## Configuration
{configuration}

## Troubleshooting
{troubleshooting}

## FAQ
{faq}

## Links
{links}
"""
        }
    
    def create_blueprint(self, 
                        config: BlueprintConfig,
                        source_filter: Optional[SourceFilter] = None,
                        use_rag: bool = True,
                        session_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a comprehensive blueprint from sources."""
        logger.info(f"Creating blueprint: {config.title}")
        
        try:
            # Step 1: Get and process sources
            sources = self.source_manager.get_sources(source_filter)
            if not sources:
                raise ValueError("No sources found matching the filter criteria")
            
            logger.info(f"Processing {len(sources)} sources for blueprint")
            
            # Step 2: Process sources and collect content
            processed_content = []
            for source in sources:
                content = self.source_manager.process_source(source.source_id)
                if content:
                    processed_content.append(content)
            
            if not processed_content:
                raise ValueError("No content could be processed from sources")
            
            # Step 3: Generate blueprint sections
            if use_rag:
                sections = self._generate_sections_with_rag(
                    processed_content, config, session_id
                )
            else:
                sections = self._generate_sections_locally(processed_content, config)
            
            # Step 4: Assemble blueprint
            blueprint = self._assemble_blueprint(sections, config, processed_content)
            
            # Step 5: Save blueprint
            output_file = self._save_blueprint(blueprint, config)
            
            logger.info(f"Blueprint created successfully: {output_file}")
            
            return {
                "status": "success",
                "title": config.title,
                "style": config.style.value,
                "format": config.format.value,
                "output_file": str(output_file),
                "sources_processed": len(processed_content),
                "sections": len(sections),
                "word_count": sum(len(section.content.split()) for section in sections),
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to create blueprint: {e}")
            return {
                "status": "error",
                "error": str(e),
                "title": config.title
            }
    
    def _generate_sections_with_rag(self, 
                                   content: List[ProcessedContent],
                                   config: BlueprintConfig,
                                   session_id: Optional[str] = None) -> List[BlueprintSection]:
        """Generate blueprint sections using n8n RAG workflow."""
        logger.info("Generating sections with RAG enhancement...")
        
        if not session_id:
            session_id = f"blueprint_{hashlib.md5(config.title.encode()).hexdigest()[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Send all content to n8n for processing
        try:
            content_summary = self._create_content_summary(content)
            self.n8n_client.send_chat_message(
                f"I'm creating a {config.style.value} blueprint titled '{config.title}'. "
                f"Here's the content summary: {content_summary}",
                session_id
            )
        except Exception as e:
            logger.warning(f"Failed to send content to n8n: {e}")
        
        # Generate sections based on style
        template_sections = self._get_template_sections(config.style)
        sections = []
        
        for section_name in template_sections:
            try:
                prompt = self._create_section_prompt(section_name, content, config)
                response = self.n8n_client.send_chat_message(prompt, session_id)
                
                section = BlueprintSection(
                    title=section_name.replace('_', ' ').title(),
                    content=response.get('response', ''),
                    subsections=[],
                    metadata={'generated_with_rag': True, 'section_type': section_name},
                    sources=[c.source_id for c in content]
                )
                sections.append(section)
                
                logger.debug(f"Generated section: {section_name}")
                
            except Exception as e:
                logger.warning(f"RAG generation failed for section {section_name}: {e}")
                # Fallback to local generation
                section = self._generate_section_locally(section_name, content, config)
                sections.append(section)
        
        return sections
    
    def _generate_sections_locally(self, 
                                  content: List[ProcessedContent],
                                  config: BlueprintConfig) -> List[BlueprintSection]:
        """Generate blueprint sections locally without RAG."""
        logger.info("Generating sections locally...")
        
        template_sections = self._get_template_sections(config.style)
        sections = []
        
        for section_name in template_sections:
            section = self._generate_section_locally(section_name, content, config)
            sections.append(section)
        
        return sections
    
    def _generate_section_locally(self, 
                                 section_name: str,
                                 content: List[ProcessedContent],
                                 config: BlueprintConfig) -> BlueprintSection:
        """Generate a single section locally."""
        # Simple local generation - combine and summarize content
        all_text = "\n\n".join([c.text_content[:1000] for c in content])
        
        section_content = f"## {section_name.replace('_', ' ').title()}\n\n"
        
        if section_name == "executive_summary":
            section_content += f"This blueprint covers {len(content)} sources related to {config.title}. "
            section_content += "Key insights and findings are presented below."
        elif section_name == "overview":
            section_content += f"Overview of {config.title} based on analysis of multiple sources."
        elif section_name == "key_findings":
            # Extract key points from all content
            key_points = []
            for c in content:
                key_points.extend(c.key_points[:3])  # Take first 3 from each
            section_content += "\n".join([f"• {point}" for point in key_points[:10]])
        else:
            section_content += f"Content for {section_name} section based on processed sources."
        
        return BlueprintSection(
            title=section_name.replace('_', ' ').title(),
            content=section_content,
            subsections=[],
            metadata={'generated_locally': True, 'section_type': section_name},
            sources=[c.source_id for c in content]
        )
    
    def _get_template_sections(self, style: BlueprintStyle) -> List[str]:
        """Get section names for a blueprint style."""
        section_mapping = {
            BlueprintStyle.COMPREHENSIVE: [
                "executive_summary", "overview", "key_findings", 
                "detailed_analysis", "recommendations", "conclusion"
            ],
            BlueprintStyle.EXECUTIVE: [
                "executive_summary", "key_points", "strategic_implications", "next_steps"
            ],
            BlueprintStyle.TECHNICAL: [
                "technical_overview", "architecture", "implementation_details", 
                "performance_analysis", "best_practices", "troubleshooting"
            ],
            BlueprintStyle.EDUCATIONAL: [
                "learning_objectives", "prerequisites", "core_concepts", 
                "step_by_step_guide", "examples", "practice_exercises"
            ],
            BlueprintStyle.REFERENCE: [
                "quick_reference", "commands_apis", "configuration", 
                "troubleshooting", "faq"
            ]
        }
        return section_mapping.get(style, ["overview", "content", "conclusion"])
    
    def _create_content_summary(self, content: List[ProcessedContent]) -> str:
        """Create a summary of all content for RAG processing."""
        summary_parts = []
        for c in content:
            summary_parts.append(f"Source {c.source_id}: {c.summary or c.text_content[:200]}...")
        return "\n".join(summary_parts)
    
    def _create_section_prompt(self, section_name: str, 
                              content: List[ProcessedContent],
                              config: BlueprintConfig) -> str:
        """Create a prompt for generating a specific section."""
        content_text = "\n\n".join([c.text_content[:1500] for c in content])
        
        return f"""
        Generate a {section_name.replace('_', ' ')} section for a {config.style.value} blueprint titled "{config.title}".
        
        Based on the following content:
        {content_text}
        
        Please create a well-structured, informative section that fits the {config.style.value} style.
        Focus on the most relevant information for the {section_name.replace('_', ' ')} section.
        """
    
    def _assemble_blueprint(self, 
                           sections: List[BlueprintSection],
                           config: BlueprintConfig,
                           content: List[ProcessedContent]) -> str:
        """Assemble the final blueprint document."""
        template = self.templates[config.style]
        
        # Create section content mapping
        section_content = {}
        for section in sections:
            key = section.metadata.get('section_type', section.title.lower().replace(' ', '_'))
            section_content[key] = section.content
        
        # Generate table of contents if requested
        toc = ""
        if config.include_toc:
            toc = "\n".join([f"- {section.title}" for section in sections])
        
        # Generate sources list if requested
        sources_list = ""
        if config.include_sources:
            sources_list = "\n".join([
                f"- {c.source_id}: {c.content_type}" for c in content
            ])
        
        # Fill template
        try:
            blueprint = template.format(
                title=config.title,
                toc=toc,
                sources=sources_list,
                **section_content
            )
        except KeyError as e:
            logger.warning(f"Template key missing: {e}, using fallback")
            # Fallback: just concatenate sections
            blueprint = f"# {config.title}\n\n"
            if toc:
                blueprint += f"## Table of Contents\n{toc}\n\n"
            for section in sections:
                blueprint += f"{section.content}\n\n"
            if sources_list:
                blueprint += f"## Sources\n{sources_list}\n"
        
        return blueprint
    
    def _save_blueprint(self, blueprint: str, config: BlueprintConfig) -> Path:
        """Save the blueprint to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"blueprint_{config.title.replace(' ', '_')}_{timestamp}"
        
        if config.format == BlueprintFormat.MARKDOWN:
            output_file = self.output_dir / f"{filename}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(blueprint)
        elif config.format == BlueprintFormat.JSON:
            output_file = self.output_dir / f"{filename}.json"
            blueprint_data = {
                "title": config.title,
                "style": config.style.value,
                "content": blueprint,
                "created_at": datetime.now().isoformat(),
                "metadata": {
                    "format": config.format.value,
                    "include_toc": config.include_toc,
                    "include_sources": config.include_sources
                }
            }
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(blueprint_data, f, indent=2, ensure_ascii=False)
        else:
            # For other formats, save as markdown for now
            output_file = self.output_dir / f"{filename}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(blueprint)
        
        return output_file
    
    def list_blueprints(self) -> List[Dict[str, Any]]:
        """List all generated blueprints."""
        blueprints = []
        
        for file_path in self.output_dir.glob("blueprint_*.md"):
            try:
                stat = file_path.stat()
                blueprints.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except Exception as e:
                logger.warning(f"Failed to get info for {file_path}: {e}")
        
        # Sort by creation time (newest first)
        blueprints.sort(key=lambda x: x["created_at"], reverse=True)
        return blueprints


# Global blueprint generator instance
_blueprint_generator = None

def get_blueprint_generator() -> BlueprintGenerator:
    """Get or create the global blueprint generator instance."""
    global _blueprint_generator
    if _blueprint_generator is None:
        _blueprint_generator = BlueprintGenerator()
    return _blueprint_generator
