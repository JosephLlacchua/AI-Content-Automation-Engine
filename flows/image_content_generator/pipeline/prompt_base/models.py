import json
from enum import Enum
from typing import Any, Dict, List, Type

from pydantic import BaseModel, Field


class Subject(BaseModel):
    description: str = Field(description="Physical description in ENGLISH. Include clothing, key features, and expression. IMPORTANT: This MUST align with the global 'style' (e.g., if stickman, keep outlines thick and features stylized).")  # noqa: E501
    action: str = Field(description="Specific action, pose, or interaction with other subjects in ENGLISH")  # noqa: E501


class ImagePrompt(BaseModel):
    subjects: List[Subject] = Field(description="List of the main subjects present in the scene")
    environment: str = Field(description="Location and background details in ENGLISH (e.g. professional office, busy street, cozy room). Style it to match the global 'style'.")  # noqa: E501
    lighting: str = Field(description="Lighting mood and color palette in ENGLISH")
    composition: str = Field(description="Shot framing and camera angle (e.g. Close-up, Wide shot) in ENGLISH")  # noqa: E501
    style: str = Field(description="EXACT visual style in ENGLISH. Match the specific visual identity requested (e.g. 'Modern webcomic sketch style').")  # noqa: E501
    aspect_ratio: str = Field(description="Aspect ratio for image generation (e.g. '9:16' for vertical shorts, '16:9' for horizontal). Must match the target video format.")  # noqa: E501

    @property
    def formatted_prompt(self) -> str:
        """
        Dynamically builds the prompt string from the structured image prompt fields.
        """
        prompt_parts: List[str] = []

        # 1. Subjects description and specific actions
        if self.subjects:
            subj_desc: List[str] = []
            for s in self.subjects:
                subj_desc.append(f"{s.description.strip()} ({s.action.strip()})")
            prompt_parts.append(f"Subjects: {'; '.join(subj_desc)}")

        # 2. Other fields
        # Dynamically handle other string fields (environment, lighting, composition)
        for key, value in self.model_dump().items():
            if key == "subjects":
                continue
            if value and isinstance(value, str):
                prompt_parts.append(f"{key.capitalize()}: {value.strip()}")

        return ". ".join(prompt_parts) + "."


class VideoPrompt(BaseModel):
    motion: str = Field(description="Movement of subjects in the scene in ENGLISH (e.g. 'Character walks forward, coins falling around him')")  # noqa: E501
    camera_movement: str = Field(description="Camera action in ENGLISH (e.g. 'Slow zoom in', 'Pan left to right', 'Static wide shot', 'Tracking shot')")  # noqa: E501
    transition: str = Field(description="How this scene transitions to the next in ENGLISH (e.g. 'Hard cut', 'Fade to black', 'Dissolve', 'Whip pan')")  # noqa: E501
    duration_hint: str = Field(description="Duration pacing and rhythm of the scene in ENGLISH (e.g. 'Fast paced', 'Slow and cinematic', '3 seconds')")  # noqa: E501


class SFXTag(str, Enum):
    """Sound effect tag that the AI assigns to each scene."""
    IMPACT       = "impact"        # Dramatic hit — hook, strong data point, narrative turn
    WHOOSH       = "whoosh"        # Fast transition between ideas, flashback, time-jump
    RISER        = "riser"         # Building tension 1-2 scenes before a climax or reveal
    GASP         = "gasp"          # Surprise, humor, exaggerated reaction, shocking stat
    POP          = "pop"           # New concept intro, list item, solution appearance on screen
    FLASH        = "flash"         # Powerful conclusion, call-to-action, memorable close
    NOTIFICATION = "notification"  # Brilliant idea, insight, "Eureka!" moment
    TYPING       = "typing"        # Text appearing on screen, CTA message, code, writing
    GLITCH       = "glitch"        # System failure, something goes wrong, error state
    MONEY        = "money"         # Money, investment, income, economic transaction
    SCRATCH      = "scratch"       # Rewind, "wait a moment", quick correction, rollback
    NONE         = "none"          # No effect — calm development scenes



class Scene(BaseModel):
    scene_number: int = Field(description="Sequential number of the scene (Integer)")
    image_prompt: ImagePrompt = Field(description="Structured details for image generation")
    video_prompt: VideoPrompt = Field(description="Structured details for video generation")
    narration: str = Field(description="Spoken narration for this scene in SPANISH (LATAM)")
    sfx_tag: SFXTag = Field(
        default=SFXTag.NONE,
        description=(
            "Sound effect type to play at the START of this scene. "
            "Choose ONE: "
            "'impact' (hook/strong data/narrative turn), "
            "'whoosh' (fast transition/flashback/time-jump), "
            "'riser' (1-2 scenes BEFORE the climax, builds tension), "
            "'gasp' (surprise/humor/shocking stat, use max 2x), "
            "'pop' (new concept appears/list item/solution shown on screen), "
            "'flash' (conclusion/CTA/memorable close), "
            "'notification' (brilliant idea/insight/eureka moment), "
            "'typing' (text on screen/CTA message/code/writing), "
            "'glitch' (error/failure/something goes wrong), "
            "'money' (money/investment/income/economic transaction), "
            "'scratch' (rewind/correction/rollback/wait a moment), "
            "'none' (calm development, no notable event)."
        ),
    )


class VideoScript(BaseModel):
    scenes: List[Scene]

    @classmethod
    def get_json_format_instructions(cls) -> str:
        """
        Returns the mandatory JSON format for the script.
        This is standardized for all script generations.
        """

        def get_format_recursive(model_class: Type[BaseModel]) -> Dict[str, Any]:
            format_dict: Dict[str, Any] = {}
            for name, field in model_class.model_fields.items():
                # Get the underlying type, handling List and Optional
                annotation = field.annotation
                origin = getattr(annotation, "__origin__", None)
                args = getattr(annotation, "__args__", (None,))

                if origin is list:
                    # Assume list of models or primitives
                    item_type = args[0]
                    if isinstance(item_type, type):
                        if issubclass(item_type, BaseModel):
                            format_dict[name] = [get_format_recursive(item_type)]
                        else:
                            format_dict[name] = [field.description or item_type.__name__]
                    else:
                        format_dict[name] = [field.description or str(item_type)]
                elif isinstance(annotation, type) and issubclass(annotation, BaseModel):
                    format_dict[name] = get_format_recursive(annotation)
                else:
                    format_dict[name] = field.description or name
            return format_dict

        # Generate sample structure
        sample_dict = get_format_recursive(cls)
        json_format = json.dumps(sample_dict, indent=2, ensure_ascii=False)

        schema_block = (
            "\n**Formato de Salida Obligatorio (JSON):**\n"
            "```json\n"
            f"{json_format}\n"
            "```\n"
        )
        return schema_block
