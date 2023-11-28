from . import APIRouter, status, Body, Depends, get_current_user, UUID, AdminUserProfile
import groundible_admin.schemas.mooyi_surveys.survey_schemas as mooyi_schemas
import groundible_admin.services.survey_service as survey_service

api_router = APIRouter(prefix="/v1/survey", tags=["Survey Managements"])


@api_router.post(
    path="/create",
    status_code=status.HTTP_201_CREATED,
    # response_model=mooyi_schemas.SurveyDetailResponse,
)
async def create_survey(
    survey: mooyi_schemas.Survey,
    admin_profile: AdminUserProfile = Depends(get_current_user),
):
    return await survey_service.create_survey(
        survey=survey, admin_uid=admin_profile.admin_uid
    )


@api_router.post(
    path="/create-target/{survey_id}",
    status_code=status.HTTP_200_OK,
    # response_model=mooyi_schemas.SurveyDetailResponse,
)
async def create_survey_target(
    survey_id: str,
    admin_profile: AdminUserProfile = Depends(get_current_user),
):
    return await survey_service.create_survey_target(survey_id=survey_id)


@api_router.post(
    path="/create-question/{survey_id}",
    status_code=status.HTTP_201_CREATED,
)
async def create_question(
    survey_id: str,
    survey_question: mooyi_schemas.SurveyQuestion,
    admin_profile: AdminUserProfile = Depends(get_current_user),
):
    return await survey_service.create_survey_questions(
        survey_id=survey_id, survey_question=survey_question
    )


@api_router.get(
    path="s/{survey_id}",
    status_code=status.HTTP_200_OK,
)
async def get_survey(
    survey_id: str,
    admin_profile: AdminUserProfile = Depends(get_current_user),
):
    return await survey_service.get_survey_by_id(
        survey_id=survey_id, admin_uid=admin_profile.admin_uid
    )
