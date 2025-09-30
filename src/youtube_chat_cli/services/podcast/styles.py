"""
Podcast style definitions and configurations.
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


class PodcastStyle(Enum):
    """Available podcast styles."""
    SUMMARY = "summary"
    DETAILED = "detailed"
    QA = "qa"
    ANALYSIS = "analysis"
    INTERVIEW = "interview"
    DEBATE = "debate"
    NEWS_REPORT = "news_report"
    EDUCATIONAL = "educational"
    STORYTELLING = "storytelling"
    PANEL = "panel"
    DOCUMENTARY = "documentary"
    QUICK_TIPS = "quick_tips"
    DEEP_DIVE = "deep_dive"
    ROUNDUP = "roundup"


class PodcastLength(Enum):
    """Podcast length categories."""
    SHORT = "short"      # 3-5 minutes
    MEDIUM = "medium"    # 10-15 minutes
    LONG = "long"        # 20-30 minutes
    EXTENDED = "extended" # 30+ minutes


class PodcastTone(Enum):
    """Podcast tone variations."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    ENTHUSIASTIC = "enthusiastic"
    EDUCATIONAL = "educational"
    CONVERSATIONAL = "conversational"
    AUTHORITATIVE = "authoritative"
    FRIENDLY = "friendly"
    DRAMATIC = "dramatic"


@dataclass
class VoiceRole:
    """Voice role configuration for multi-speaker podcasts."""
    name: str
    voice_id: str
    description: str
    personality: str


@dataclass
class PodcastStyleConfig:
    """Configuration for a podcast style."""
    name: str
    description: str
    typical_length: Dict[PodcastLength, int]  # Length in seconds
    voice_roles: List[VoiceRole]
    tone_options: List[PodcastTone]
    structure_template: str
    prompt_template: str


class PodcastStyleManager:
    """Manager for podcast styles and configurations."""
    
    def __init__(self):
        self.styles = self._initialize_styles()
    
    def _initialize_styles(self) -> Dict[PodcastStyle, PodcastStyleConfig]:
        """Initialize all podcast style configurations."""
        return {
            PodcastStyle.SUMMARY: PodcastStyleConfig(
                name="Summary",
                description="Quick overview of main points",
                typical_length={
                    PodcastLength.SHORT: 180,    # 3 minutes
                    PodcastLength.MEDIUM: 600,   # 10 minutes
                    PodcastLength.LONG: 1200,    # 20 minutes
                    PodcastLength.EXTENDED: 1800 # 30 minutes
                },
                voice_roles=[
                    VoiceRole("narrator", "en-US-AriaNeural", "Main narrator", "clear and informative")
                ],
                tone_options=[PodcastTone.PROFESSIONAL, PodcastTone.EDUCATIONAL, PodcastTone.CASUAL],
                structure_template="introduction -> key_points -> conclusion",
                prompt_template="Create a concise summary podcast covering the main points of: {content}"
            ),
            
            PodcastStyle.INTERVIEW: PodcastStyleConfig(
                name="Interview",
                description="Conversational format between host and expert",
                typical_length={
                    PodcastLength.SHORT: 300,    # 5 minutes
                    PodcastLength.MEDIUM: 900,   # 15 minutes
                    PodcastLength.LONG: 1800,    # 30 minutes
                    PodcastLength.EXTENDED: 2700 # 45 minutes
                },
                voice_roles=[
                    VoiceRole("host", "en-US-JennyNeural", "Podcast host", "engaging and curious"),
                    VoiceRole("expert", "en-US-GuyNeural", "Subject matter expert", "knowledgeable and authoritative")
                ],
                tone_options=[PodcastTone.CONVERSATIONAL, PodcastTone.FRIENDLY, PodcastTone.PROFESSIONAL],
                structure_template="introduction -> interview_questions -> expert_responses -> wrap_up",
                prompt_template="Create an interview-style podcast with questions and answers about: {content}"
            ),
            
            PodcastStyle.DEBATE: PodcastStyleConfig(
                name="Debate",
                description="Multiple perspectives on the topic",
                typical_length={
                    PodcastLength.SHORT: 420,    # 7 minutes
                    PodcastLength.MEDIUM: 1200,  # 20 minutes
                    PodcastLength.LONG: 2400,    # 40 minutes
                    PodcastLength.EXTENDED: 3600 # 60 minutes
                },
                voice_roles=[
                    VoiceRole("moderator", "en-US-AriaNeural", "Debate moderator", "neutral and professional"),
                    VoiceRole("advocate", "en-US-JennyNeural", "Position advocate", "passionate and persuasive"),
                    VoiceRole("critic", "en-US-GuyNeural", "Position critic", "analytical and challenging")
                ],
                tone_options=[PodcastTone.PROFESSIONAL, PodcastTone.AUTHORITATIVE, PodcastTone.DRAMATIC],
                structure_template="introduction -> position_statements -> rebuttals -> conclusion",
                prompt_template="Create a debate-style podcast exploring different perspectives on: {content}"
            ),
            
            PodcastStyle.NEWS_REPORT: PodcastStyleConfig(
                name="News Report",
                description="Journalistic coverage style",
                typical_length={
                    PodcastLength.SHORT: 240,    # 4 minutes
                    PodcastLength.MEDIUM: 720,   # 12 minutes
                    PodcastLength.LONG: 1440,    # 24 minutes
                    PodcastLength.EXTENDED: 2160 # 36 minutes
                },
                voice_roles=[
                    VoiceRole("anchor", "en-US-AriaNeural", "News anchor", "authoritative and clear"),
                    VoiceRole("reporter", "en-US-JennyNeural", "Field reporter", "informative and engaging")
                ],
                tone_options=[PodcastTone.PROFESSIONAL, PodcastTone.AUTHORITATIVE, PodcastTone.EDUCATIONAL],
                structure_template="headline -> background -> details -> implications -> conclusion",
                prompt_template="Create a news report style podcast covering: {content}"
            ),
            
            PodcastStyle.EDUCATIONAL: PodcastStyleConfig(
                name="Educational Lecture",
                description="Teaching-focused presentation",
                typical_length={
                    PodcastLength.SHORT: 360,    # 6 minutes
                    PodcastLength.MEDIUM: 1080,  # 18 minutes
                    PodcastLength.LONG: 2160,    # 36 minutes
                    PodcastLength.EXTENDED: 3240 # 54 minutes
                },
                voice_roles=[
                    VoiceRole("instructor", "en-US-AriaNeural", "Course instructor", "patient and knowledgeable")
                ],
                tone_options=[PodcastTone.EDUCATIONAL, PodcastTone.PROFESSIONAL, PodcastTone.FRIENDLY],
                structure_template="learning_objectives -> concepts -> examples -> practice -> summary",
                prompt_template="Create an educational lecture podcast teaching about: {content}"
            ),
            
            PodcastStyle.STORYTELLING: PodcastStyleConfig(
                name="Storytelling Narrative",
                description="Story-driven content",
                typical_length={
                    PodcastLength.SHORT: 420,    # 7 minutes
                    PodcastLength.MEDIUM: 1260,  # 21 minutes
                    PodcastLength.LONG: 2520,    # 42 minutes
                    PodcastLength.EXTENDED: 3780 # 63 minutes
                },
                voice_roles=[
                    VoiceRole("narrator", "en-US-AriaNeural", "Story narrator", "engaging and dramatic")
                ],
                tone_options=[PodcastTone.DRAMATIC, PodcastTone.CONVERSATIONAL, PodcastTone.ENTHUSIASTIC],
                structure_template="setup -> conflict -> development -> climax -> resolution",
                prompt_template="Create a narrative storytelling podcast about: {content}"
            ),
            
            PodcastStyle.PANEL: PodcastStyleConfig(
                name="Panel Discussion",
                description="Multiple speakers discussing the topic",
                typical_length={
                    PodcastLength.SHORT: 480,    # 8 minutes
                    PodcastLength.MEDIUM: 1440,  # 24 minutes
                    PodcastLength.LONG: 2880,    # 48 minutes
                    PodcastLength.EXTENDED: 4320 # 72 minutes
                },
                voice_roles=[
                    VoiceRole("moderator", "en-US-AriaNeural", "Panel moderator", "organized and fair"),
                    VoiceRole("panelist1", "en-US-JennyNeural", "First panelist", "thoughtful and articulate"),
                    VoiceRole("panelist2", "en-US-GuyNeural", "Second panelist", "insightful and experienced"),
                    VoiceRole("panelist3", "en-US-DavisNeural", "Third panelist", "creative and innovative")
                ],
                tone_options=[PodcastTone.CONVERSATIONAL, PodcastTone.PROFESSIONAL, PodcastTone.FRIENDLY],
                structure_template="introductions -> topic_discussion -> individual_perspectives -> group_synthesis",
                prompt_template="Create a panel discussion podcast with multiple perspectives on: {content}"
            ),
            
            PodcastStyle.DOCUMENTARY: PodcastStyleConfig(
                name="Documentary",
                description="In-depth investigative format",
                typical_length={
                    PodcastLength.SHORT: 600,    # 10 minutes
                    PodcastLength.MEDIUM: 1800,  # 30 minutes
                    PodcastLength.LONG: 3600,    # 60 minutes
                    PodcastLength.EXTENDED: 5400 # 90 minutes
                },
                voice_roles=[
                    VoiceRole("narrator", "en-US-AriaNeural", "Documentary narrator", "authoritative and compelling")
                ],
                tone_options=[PodcastTone.AUTHORITATIVE, PodcastTone.DRAMATIC, PodcastTone.PROFESSIONAL],
                structure_template="introduction -> investigation -> evidence -> analysis -> conclusion",
                prompt_template="Create a documentary-style podcast investigating: {content}"
            ),
            
            PodcastStyle.QUICK_TIPS: PodcastStyleConfig(
                name="Quick Tips",
                description="Short, actionable advice format",
                typical_length={
                    PodcastLength.SHORT: 120,    # 2 minutes
                    PodcastLength.MEDIUM: 360,   # 6 minutes
                    PodcastLength.LONG: 720,     # 12 minutes
                    PodcastLength.EXTENDED: 1080 # 18 minutes
                },
                voice_roles=[
                    VoiceRole("host", "en-US-JennyNeural", "Tips host", "energetic and helpful")
                ],
                tone_options=[PodcastTone.ENTHUSIASTIC, PodcastTone.FRIENDLY, PodcastTone.CASUAL],
                structure_template="intro -> tip1 -> tip2 -> tip3 -> action_steps",
                prompt_template="Create a quick tips podcast with actionable advice about: {content}"
            ),
            
            PodcastStyle.DEEP_DIVE: PodcastStyleConfig(
                name="Deep Dive",
                description="Extended technical analysis",
                typical_length={
                    PodcastLength.SHORT: 900,    # 15 minutes
                    PodcastLength.MEDIUM: 2700,  # 45 minutes
                    PodcastLength.LONG: 5400,    # 90 minutes
                    PodcastLength.EXTENDED: 7200 # 120 minutes
                },
                voice_roles=[
                    VoiceRole("analyst", "en-US-GuyNeural", "Technical analyst", "thorough and methodical")
                ],
                tone_options=[PodcastTone.PROFESSIONAL, PodcastTone.AUTHORITATIVE, PodcastTone.EDUCATIONAL],
                structure_template="background -> methodology -> detailed_analysis -> implications -> future_directions",
                prompt_template="Create a comprehensive deep-dive analysis podcast about: {content}"
            ),
            
            PodcastStyle.ROUNDUP: PodcastStyleConfig(
                name="Roundup",
                description="Compilation of multiple sources",
                typical_length={
                    PodcastLength.SHORT: 480,    # 8 minutes
                    PodcastLength.MEDIUM: 1440,  # 24 minutes
                    PodcastLength.LONG: 2880,    # 48 minutes
                    PodcastLength.EXTENDED: 4320 # 72 minutes
                },
                voice_roles=[
                    VoiceRole("host", "en-US-AriaNeural", "Roundup host", "organized and comprehensive")
                ],
                tone_options=[PodcastTone.PROFESSIONAL, PodcastTone.EDUCATIONAL, PodcastTone.CONVERSATIONAL],
                structure_template="overview -> source1_summary -> source2_summary -> synthesis -> conclusions",
                prompt_template="Create a roundup podcast summarizing multiple sources about: {content}"
            )
        }
    
    def get_style_config(self, style: PodcastStyle) -> PodcastStyleConfig:
        """Get configuration for a specific podcast style."""
        return self.styles[style]
    
    def get_available_styles(self) -> List[str]:
        """Get list of available podcast style names."""
        return [style.value for style in PodcastStyle]
    
    def get_style_description(self, style: PodcastStyle) -> str:
        """Get description for a podcast style."""
        return self.styles[style].description
    
    def get_estimated_duration(self, style: PodcastStyle, length: PodcastLength) -> int:
        """Get estimated duration in seconds for a style and length combination."""
        return self.styles[style].typical_length[length]
    
    def get_voice_roles(self, style: PodcastStyle) -> List[VoiceRole]:
        """Get voice roles for a podcast style."""
        return self.styles[style].voice_roles
    
    def get_tone_options(self, style: PodcastStyle) -> List[PodcastTone]:
        """Get available tone options for a podcast style."""
        return self.styles[style].tone_options


# Global style manager instance
_style_manager = None

def get_style_manager() -> PodcastStyleManager:
    """Get or create the global podcast style manager instance."""
    global _style_manager
    if _style_manager is None:
        _style_manager = PodcastStyleManager()
    return _style_manager
