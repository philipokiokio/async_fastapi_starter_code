from httpx import AsyncClient
from groundible_admin.root.settings import Settings
from groundible_admin.schemas.mooyi_surveys import survey_schemas as schemas
from datetime import datetime

settings = Settings()
MOOYI_ENDPOINT = settings.mooyi_survey

ASYNC_CLIENT = AsyncClient()
ASYNC_CLIENT.headers = {
    "workspace": settings.mooyi_workspace_token,
    "Authorization": f"Bearer {settings.mooyi_groundible_token}",
}


async def create_survey_detail(survey_detail: schemas.Survey):
    survey_detail_payload = {
        "surveyName": survey_detail.survey_name,
        "surveyCategory": survey_detail.survey_category,
        "surveyDescription": survey_detail.survey_description,
        "coverImage": survey_detail.cover_image,
        "businessLogo": survey_detail.business_logo,
        "templateName": survey_detail.template_name,
    }

    survey_detail_payload["screenQue"] = {
        "toggle": survey_detail.pre_feteched_option,
        "question": survey_detail.pre_feteched_question,
        "options": survey_detail.pre_feteched_option,
        "disqualifier": survey_detail.pre_feteched_disqualifier,
    }
    survey_detail_resp = await ASYNC_CLIENT.post(
        url=f"{MOOYI_ENDPOINT}/survey-microservice/survey/create-details",
        json=survey_detail_payload,
    )
    print(survey_detail_resp.json())
    return schemas.SurveyDetailResponse(**survey_detail_resp.json()["data"])


async def create_survey_target(survey_id: str):
    survey_target_resp = await ASYNC_CLIENT.post(
        url=f"{MOOYI_ENDPOINT}/survey-microservice/survey/create-targetopt/{survey_id}",
        json={
            "audienceType": "generate_link",
            "expectedResponse": 1000000,
            "reward": 0,
            "sendReminderAfter24hrs": False,
            "shareToPublic": True,
            "saveLeads": True,
        },
    )

    return schemas.SurveyQuestionResponse(**survey_target_resp.json()["data"])


async def create_survey_question(
    survey_id: str, suvery_question: schemas.SurveyQuestion
):
    survey_question_payload = suvery_question.model_dump()

    survey_question_resp = await ASYNC_CLIENT.post(
        url=f"{MOOYI_ENDPOINT}/survey-microservice/survey/create-questions/{survey_id}",
        json=survey_question_payload,
    )

    return schemas.SurveyQuestionResponse(**survey_question_resp.json()["data"])


async def publish_survey(
    survey_id: str, published_date: datetime, schedule_for_later: bool = False
):
    survey_detail_resp = await ASYNC_CLIENT.post(
        url=f"{MOOYI_ENDPOINT}/survey-microservice/survey/publish/{survey_id}",
        json={"publishDate": published_date, "scheduleForLater": schedule_for_later},
    )

    return schemas.SurveyQuestionResponse(**survey_detail_resp.json()["data"])


async def get_survey_by_survey_id(survey_id: str):
    survey_detail_resp = await ASYNC_CLIENT.get(
        url=f"{MOOYI_ENDPOINT}/survey-microservice/survey/single/{survey_id}",
    )
    print(
        schemas.SurveyQuestionResponse(**survey_detail_resp.json()["data"]).model_dump()
    )
    return schemas.SurveyQuestionResponse(**survey_detail_resp.json()["data"])
