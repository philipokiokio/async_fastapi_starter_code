from groundible_admin.schemas import AbstractModel, Optional, List, Union
from pydantic import AnyHttpUrl, Field
from enum import Enum


def camel_to_snake(string):
    return "".join(["_" + char.lower() if char.isupper() else char for char in string])


class CamelCaseOveride(AbstractModel):
    class Config:
        alias_generator = lambda string: string.lstrip("_")

    def model_dump(self, *args, **kwargs):
        snake_case_dict = {
            camel_to_snake(key): value
            for key, value in super().model_dump(*args, **kwargs).items()
        }
        return snake_case_dict


class Survey(AbstractModel):
    """Route level"""

    survey_name: str
    survey_category: str
    survey_description: Optional[str] = None
    cover_image: Optional[str] = None
    business_logo: Optional[str] = None
    template_name: Optional[str] = None
    add_screen_que: bool = False
    pre_feteched_question: Optional[str] = None
    pre_feteched_option: Optional[List[str]] = None
    pre_feteched_disqualifier: Optional[str] = None


class SurveyDetail(CamelCaseOveride):
    survey_name: str = Field(alias="surveyName")
    survey_category: str = Field(alias="surveyCategory")
    survey_description: Union[str, None] = Field(alias="surveyDescription")
    cover_image: Union[str, None] = Field(alias="coverImage")
    business_logo: Union[str, None] = Field(alias="businessLogo")
    template_name: Union[str, None] = Field(alias="templateName")


class SurveyDetailResponse(CamelCaseOveride):
    id: str = Field(alias="_id")
    survey_details: SurveyDetail = Field(alias="surveyDetails")
    survey_status: str = Field(alias="surveyStatus")
    publish_date: Union[str, None] = Field(alias="publishDate")
    active_at: Union[str, None] = Field(alias="activeAt")
    closed_at: Union[str, None] = Field(alias="closedAt")
    completed_at: Union[str, None] = Field(alias="completedAt")


class QuestionType(Enum):
    text_response = "text_response"
    single_choice = "single_choice"
    multi_choice = "multi_choice"
    image = "image"
    likert = "likert"


class LikertValue(AbstractModel):
    value: int
    label: str


class Likert(AbstractModel):
    max: LikertValue
    min: LikertValue


class Question(AbstractModel):
    question: str
    optional: bool
    question_type: QuestionType
    options: Optional[Union[List[str], Likert]] = None


class SurveyQuestion(AbstractModel):
    questions: Optional[Union[List[Question], None]]

    # "targetingOption": {
    #     "audienceType": "generate_link",
    #     "expectedResponse": 1000000,
    #     "reward": 0,
    #     "sendReminderAfter24hrs": false,
    #     "shareToPublic": true,
    #     "saveLeads": true,
    #     "rewardedCount": 0
    # }


class TargetOptionResponse(CamelCaseOveride):
    audience_type: str = Field(alias="audienceType")
    expected_response: int = Field(alias="expectedResponse")
    reward: int
    send_reminder_after_24_hrs: bool = Field(alias="sendReminderAfter24hrs")
    share_to_public: bool = Field(alias="shareToPublic")
    rewarded_count: int = Field(alias="rewardedCount")


class SurveyTarget(CamelCaseOveride):
    target_option: Optional[Union[TargetOptionResponse, None]] = Field(
        alias="targetingOption"
    )
    ...


class SurveyQuestionResponse(
    SurveyDetailResponse, SurveyTarget, SurveyQuestion, CamelCaseOveride
):
    cost: int = 0
    survey_status: str = Field(alias="surveyStatus")
