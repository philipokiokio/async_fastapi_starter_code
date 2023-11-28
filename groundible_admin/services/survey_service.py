import groundible_admin.schemas.mooyi_surveys.survey_schemas as mooyi_schemas
from groundible_admin.services import HTTPException, UUID
import groundible_admin.services.service_utils.survey_utils as survey_utils
from datetime import datetime


async def create_survey(survey: mooyi_schemas.Survey, admin_uid: UUID):
    survey_detail = await survey_utils.create_survey_detail(survey_detail=survey)
    return survey_detail.model_dump()


async def create_survey_target(survey_id: str):
    survey_target = await survey_utils.create_survey_target(survey_id=survey_id)
    return survey_target.model_dump()


async def create_survey_questions(
    survey_id: str, survey_question: mooyi_schemas.SurveyQuestion
):
    survey_question = await survey_utils.create_survey_question(
        survey_id=survey_id, suvery_question=survey_question
    )
    return survey_question.model_dump()


async def publish_survey(
    survey_id: str, published_date: datetime, schedule_for_later: bool
):
    survey_published = await survey_utils.publish_survey(
        survey_id=survey_id,
        published_date=published_date,
        schedule_for_later=schedule_for_later,
    )

    return survey_published.model_dump()


async def get_survey_by_id(survey_id: str, admin_uid: UUID):
    survey_question_response = await survey_utils.get_survey_by_survey_id(
        survey_id=survey_id
    )

    return survey_question_response.model_dump()
