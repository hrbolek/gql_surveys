from typing import List, Union, Optional
import typing
import strawberry
import uuid

from .BaseGQLModel import BaseGQLModel, IDType
from ..Dataloaders import getLoadersFromInfo

from ._GraphResolvers import (
    resolve_id,
    resolve_name,
    resolve_lastchange,
    resolve_changedby,
    resolve_created,
    resolve_createdby
)

UserGQLModel = typing.Annotated["UserGQLModel", strawberry.lazy(".externals")]

@strawberry.federation.type(
    keys=["id"],
    description="""Entity representing a relation between an user and a group""",
)
class QuestionTypeGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info): 
        return getLoadersFromInfo(info).surveyquestiontypes

    id = resolve_id
    name = resolve_name
    
    lastchange = resolve_lastchange
    changedby = resolve_changedby
    created = resolve_created
    createdby = resolve_createdby


import datetime

@strawberry.federation.type(
    keys=["id"],
    description="""Entity representing a relation between an user and a group""",
)
class SurveyTypeGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info): 
        return getLoadersFromInfo(info).surveytypes

    id = resolve_id
    name = resolve_name
    
    lastchange = resolve_lastchange
    changedby = resolve_changedby
    created = resolve_created
    createdby = resolve_createdby

@strawberry.federation.type(
    keys=["id"],
    description="""Entity representing a relation between an user and a group""",
)
class SurveyGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info): 
        return getLoadersFromInfo(info).surveys

    id = resolve_id
    name = resolve_name
    
    lastchange = resolve_lastchange
    changedby = resolve_changedby
    created = resolve_created
    createdby = resolve_createdby

    @strawberry.field(description="""List""")
    async def questions(
        self, info: strawberry.types.Info
    ) -> typing.List["QuestionGQLModel"]:
        loader = QuestionGQLModel.getLoader(info)
        result = await loader.filter_by(survey_id=self.id)
        return result


#     @strawberry.field(description="""List""")
#     async def editor(self, info: strawberry.types.Info) -> 'SurveyEditorGQLModel':
#         return self

# @strawberry.federation.type(keys=["id"], description="""Editor""") ###############
# class SurveyEditorGQLModel:
#     pass


@strawberry.federation.type(
    keys=["id"], description="""Entity representing an access to information"""
)
class QuestionGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info): 
        return getLoadersFromInfo(info).surveyquestions

    id = resolve_id
    name = resolve_name
    
    lastchange = resolve_lastchange
    changedby = resolve_changedby
    created = resolve_created
    createdby = resolve_createdby

    @strawberry.field(description="""Order of questions""")
    def order(self) -> int:
        return self.order

    @strawberry.field(description="""List of answers""")
    async def answers(
        self, info: strawberry.types.Info
    ) -> typing.List["AnswerGQLModel"]:
        loader = AnswerGQLModel.getLoader(info)
        result = await loader.filter_by(question_id=self.id)
        return result

    @strawberry.field(description="""Survey which owns this question""")
    async def survey(
        self, info: strawberry.types.Info
    ) -> typing.Union["SurveyGQLModel", None]:
        result = await SurveyGQLModel.resolve_reference(info, self.survey_id)
        return result

    @strawberry.field(description="""Type of question""")
    async def type(
        self, info: strawberry.types.Info
    ) -> typing.Union["QuestionTypeGQLModel", None]:
        result = await QuestionTypeGQLModel.resolve_reference(info, self.type_id)
        return result

    @strawberry.field(description="""List of values for closed or similar type questions""")
    async def values(
        self, info: strawberry.types.Info
    ) -> typing.List["QuestionValueGQLModel"]:
        loader = QuestionValueGQLModel.getLoader(info)
        result = await loader.filter_by(question_id=self.id)
        return result

@strawberry.federation.type(
    keys=["id"], description="""Entity representing an access to information"""
)
class AnswerGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info): 
        return getLoadersFromInfo(info).surveyanswers

    id = resolve_id
    
    lastchange = resolve_lastchange
    changedby = resolve_changedby
    created = resolve_created
    createdby = resolve_createdby

    @strawberry.field(description="""answer content / value""")
    def value(self) -> Union[str, None]:
        return self.value

    @strawberry.field(description="""is the survey already answered?""")
    async def aswered(self) -> Union[bool, None]:
        return self.aswered

    @strawberry.field(description="""is the survey still available?""")
    async def expired(self) -> Union[bool, None]:
        return self.expired

    @strawberry.field(
        description="""is the survey still available?"""
    )  # mimo náš kontejner
    async def user(self) -> Optional[UserGQLModel]:
        from .externals import UserGQLModel
        return await UserGQLModel.resolve_reference(self.user_id)

    @strawberry.field(
        description="""is the survey still available?"""
    )  # v našem kontejneru
    async def question(self, info: strawberry.types.Info) -> QuestionGQLModel:
        return await QuestionGQLModel.resolve_reference(info, self.question_id)

@strawberry.federation.type(
    keys=["id"], description="""Entity representing an access to information"""
)
class QuestionValueGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info): 
        return getLoadersFromInfo(info).surveyquestionvalues

    id = resolve_id
    name = resolve_name
    
    lastchange = resolve_lastchange
    changedby = resolve_changedby
    created = resolve_created
    createdby = resolve_createdby

    @strawberry.field(description="""order of value""")
    def order(self) -> int:
        return self.order

    @strawberry.field(description="""Question which has this possible answer""")
    async def question(self, info: strawberry.types.Info) -> Union[QuestionGQLModel, None]:
        result = await QuestionGQLModel.resolve_reference(info, self.question_id)
        return result

##########################################
#
# queries
#
##########################################
from dataclasses import dataclass
from uoishelpers.resolvers import createInputs
from .GraphPermissions import OnlyForAuthentized
from src.DBResolvers import DBResolvers

@createInputs
@dataclass
class SurveyTypeInputWhereFilter:
    name: str
    name_en: str


survey_type_page = strawberry.field(
    description="""Returns a list of surveys' types (paged)""",
    permission_classes=[
        OnlyForAuthentized
    ],
    resolver=DBResolvers.SurveyTypeModel.resolve_page(SurveyTypeGQLModel, WhereFilterModel=SurveyTypeInputWhereFilter)
)

survey_type_by_id = strawberry.field(
    description="""Finds a survey type by its id""",
    permission_classes=[
        OnlyForAuthentized
    ],
    resolver=DBResolvers.SurveyTypeModel.resolve_by_id(SurveyTypeGQLModel)
)

@createInputs
@dataclass
class SurveyInputWhereFilter:
    name: str
    name_en: str


survey_page = strawberry.field(
    description="""Returns a list of surveys (paged)""",
    permission_classes=[
        OnlyForAuthentized
    ],
    resolver=DBResolvers.SurveyModel.resolve_page(SurveyGQLModel, WhereFilterModel=SurveyInputWhereFilter)
)

survey_by_id = strawberry.field(
    description="""Finds a survey by its id""",
    permission_classes=[
        OnlyForAuthentized
    ],
    resolver=DBResolvers.SurveyModel.resolve_by_id(SurveyGQLModel)
)

@createInputs
@dataclass
class QuestionInputWhereFilter:
    name: str
    name_en: str


question_page = strawberry.field(
    description="""Returns a list of questions (paged)""",
    permission_classes=[
        OnlyForAuthentized
    ],
    resolver=DBResolvers.QuestionModel.resolve_page(QuestionGQLModel, WhereFilterModel=QuestionInputWhereFilter)
)

question_by_id = strawberry.field(
    description="""Finds a question by its id""",
    permission_classes=[
        OnlyForAuthentized
    ],
    resolver=DBResolvers.QuestionModel.resolve_by_id(QuestionGQLModel)
)

@createInputs
@dataclass
class QuestionTypeInputWhereFilter:
    name: str
    name_en: str


question_type_page = strawberry.field(
    description="""Returns a list of question types (paged)""",
    permission_classes=[
        OnlyForAuthentized
    ],
    resolver=DBResolvers.QuestionTypeModel.resolve_page(QuestionTypeGQLModel, WhereFilterModel=QuestionTypeInputWhereFilter)
)

question_type_by_id = strawberry.field(
    description="""Finds a question type by its id""",
    permission_classes=[
        OnlyForAuthentized
    ],
    resolver=DBResolvers.QuestionTypeModel.resolve_by_id(QuestionTypeGQLModel)
)

@createInputs
@dataclass
class AnswerInputWhereFilter:
    name: str
    name_en: str
    question_id: IDType
    user_id: IDType

answer_page = strawberry.field(
    description="""Returns a list of answers (paged)""",
    permission_classes=[
        OnlyForAuthentized
    ],
    resolver=DBResolvers.AnswerModel.resolve_page(AnswerGQLModel, WhereFilterModel=AnswerInputWhereFilter)
)

answer_by_id = strawberry.field(
    description="""Finds a answer by its id""",
    permission_classes=[
        OnlyForAuthentized
    ],
    resolver=DBResolvers.AnswerModel.resolve_by_id(AnswerGQLModel)
)

# @strawberry.type(description="""Type for query root""")
# class Query:
#     @strawberry.field(description="""Page of survey types""")
#     async def survey_type_page(
#         self, info: strawberry.types.Info, skip: int = 0, limit: int = 20
#     ) -> List[SurveyTypeGQLModel]:
#         loader = SurveyTypeGQLModel.getLoader(info)
#         result = await loader.page(skip, limit)
#         return result
    
#     @strawberry.field(description="""Finds a survey type by its id""")
#     async def survey_type_by_id(
#         self, info: strawberry.types.Info, id: strawberry.ID
#     ) -> Union[SurveyTypeGQLModel, None]:
#         return await SurveyTypeGQLModel.resolve_reference(info, id)
    
#     @strawberry.field(description="""Finds a survey by its id""")
#     async def survey_by_id(
#         self, info: strawberry.types.Info, id: strawberry.ID
#     ) -> Union[SurveyGQLModel, None]:
#         return await SurveyGQLModel.resolve_reference(info, id)

#     @strawberry.field(description="""Page of surveys""")
#     async def survey_page(
#         self, info: strawberry.types.Info, skip: int = 0, limit: int = 20
#     ) -> List[SurveyGQLModel]:
#         loader = SurveyGQLModel.getLoader(info)
#         result = await loader.page(skip, limit)
#         return result
    
#     @strawberry.field(description="""Question by id""")
#     async def question_by_id(
#         self, info: strawberry.types.Info, id: strawberry.ID
#     ) -> Union[QuestionGQLModel, None]:
#         return await QuestionGQLModel.resolve_reference(info, id)

#     @strawberry.field(description="""Question type by id""")
#     async def question_type_by_id(
#         self, info: strawberry.types.Info, id: strawberry.ID
#     ) -> Union[QuestionTypeGQLModel, None]:
#         return await QuestionTypeGQLModel.resolve_reference(info, id)

#     @strawberry.field(description="""Question type by id""")
#     async def question_type_page(
#         self, info: strawberry.types.Info, skip: int = 0, limit: int = 20
#     ) -> List[QuestionTypeGQLModel]:
#         loader = QuestionTypeGQLModel.getLoader(info)
#         result = await loader.page(skip, limit)
#         return result

#     @strawberry.field(description="""Answer by id""")
#     async def answer_by_id(
#         self, info: strawberry.types.Info, id: strawberry.ID
#     ) -> Union[AnswerGQLModel, None]:
#         print(id, flush=True)
#         return await AnswerGQLModel.resolve_reference(info, id)
    

#     @strawberry.field(description="""Answer by user""")
#     async def answers_by_user(
#         self, info: strawberry.types.Info, user_id: strawberry.ID
#     ) -> Union[AnswerGQLModel, None]:
#         loader = AnswerGQLModel.getLoader(info)
#         result = await loader.filter_by(user_id=user_id)
#         return result  

    # @strawberry.field(description="""Answer by id""")
    # async def load_survey(
    #     self, info: strawberry.types.Info
    # ) -> Union[SurveyGQLModel, None]:
    #     async with withInfo(info) as session:
    #         surveyID = await randomSurveyData(AsyncSessionFromInfo(info))
    #         result = await resolveSurveyById(session, surveyID)
    #         return result


###########################################################################################################################
#
#
# Mutations
#
#
###########################################################################################################################

from typing import Optional
import datetime

@strawberry.input
class SurveyInsertGQLModel:
    name: str
    name_en: Optional[str] = ""

    type_id: Optional[strawberry.ID] = None
    id: Optional[strawberry.ID] = None

@strawberry.input
class SurveyUpdateGQLModel:
    lastchange: datetime.datetime
    id: strawberry.ID
    name: Optional[str] = None
    name_en: Optional[str] = None
    type_id: Optional[strawberry.ID] = None
    
@strawberry.type
class SurveyResultGQLModel:
    id: strawberry.ID = None
    msg: str = None

    @strawberry.field(description="""Result of survey operation""")
    async def survey(self, info: strawberry.types.Info) -> Union[SurveyGQLModel, None]:
        result = await SurveyGQLModel.resolve_reference(info, self.id)
        return result

@strawberry.mutation(description="""Creates new survey""")
async def survey_insert(self, info: strawberry.types.Info, survey: SurveyInsertGQLModel) -> SurveyResultGQLModel:
    loader = getLoaders(info).surveys
    row = await loader.insert(survey)
    result = SurveyResultGQLModel()
    result.msg = "ok"
    result.id = row.id
    return result

@strawberry.mutation(description="""Updates the survey""")
async def survey_update(self, info: strawberry.types.Info, survey: SurveyUpdateGQLModel) -> SurveyResultGQLModel:
    loader = getLoaders(info).surveys
    row = await loader.update(survey)
    result = SurveyResultGQLModel()
    result.msg = "ok"
    result.id = survey.id
    if row is None:
        result.msg = "fail"           
    return result

@strawberry.mutation(description="""Assigns the survey to the user. For all questions in the survey are created empty answers for the user.""")
async def survey_assing_to(self, info: strawberry.types.Info, survey_id: strawberry.ID, user_id: strawberry.ID) -> SurveyResultGQLModel:
    loader = getLoaders(info).questions
    questions = await loader.filter_by(survey_id=survey_id)
    loader = getLoaders(info).answers
    for q in questions:
        exists = await loader.filter_by(question_id=q.id, user_id=user_id)
        if next(exists, None) is None:
            #user has not this particular question
            rowa = await loader.insert(None, {"question_id": q.id, "user_id": user_id})
    result = SurveyResultGQLModel()
    result.msg = "ok"
    result.id = survey_id
        
    return result

@strawberry.input
class AnswerUpdateGQLModel:
    lastchange: datetime.datetime
    id: strawberry.ID
    value: Optional[str] = None
    aswered: Optional[bool] = None   
    expired: Optional[bool] = None   
    
@strawberry.type
class AnswerResultGQLModel:
    id: strawberry.ID = None
    msg: str = None

    @strawberry.field(description="""Result of answer operation""")
    async def answer(self, info: strawberry.types.Info) -> Union[AnswerGQLModel, None]:
        result = await AnswerGQLModel.resolve_reference(info, self.id)
        return result

@strawberry.mutation(description="""Allows update a question.""")
async def answer_update(self, info: strawberry.types.Info, answer: AnswerUpdateGQLModel) -> AnswerResultGQLModel:
    loader = getLoaders(info).answers
    row = await loader.update(answer)
    result = AnswerResultGQLModel()
    result.msg = "ok"
    result.id = answer.id
    if row is None:
        result.msg = "fail"           
    return result

@strawberry.input
class QuestionInsertGQLModel:
    name: str
    survey_id: strawberry.ID
    name_en: Optional[str] = ""
    type_id: Optional[strawberry.ID] = None
    order: Optional[int] = 1
    id: Optional[strawberry.ID] = None

@strawberry.input
class QuestionUpdateGQLModel:
    lastchange: datetime.datetime
    id: strawberry.ID
    name: Optional[str] = None
    name_en: Optional[str] = None
    type_id: Optional[strawberry.ID] = None
    order: Optional[int] = None

@strawberry.type
class QuestionResultGQLModel:
    id: strawberry.ID = None
    msg: str = None

    @strawberry.field(description="""Result of question operation""")
    async def question(self, info: strawberry.types.Info) -> Union[QuestionGQLModel, None]:
        result = await QuestionGQLModel.resolve_reference(info, self.id)
        return result

@strawberry.mutation(description="""Creates new question in the survey""")
async def question_insert(self, info: strawberry.types.Info, question: QuestionInsertGQLModel) -> QuestionResultGQLModel:
    loader = getLoaders(info).questions
    row = await loader.insert(question)
    result = QuestionResultGQLModel()
    result.msg = "ok"
    result.id = row.id
    return result

@strawberry.mutation(description="""Updates question""")
async def question_update(self, info: strawberry.types.Info, question: QuestionUpdateGQLModel) -> QuestionResultGQLModel:
    loader = getLoaders(info).questions
    row = await loader.update(question)
    result = QuestionResultGQLModel()
    result.msg = "ok"
    result.id = question.id
    if row is None:
        result.msg = "fail"           
    return result


@strawberry.input
class QuestionValueInsertGQLModel:
    question_id: strawberry.ID
    name: str
    name_en: Optional[str] = ""   
    order: Optional[int] = 1
    id: Optional[strawberry.ID] = None

@strawberry.input
class QuestionValueUpdateGQLModel:
    lastchange: datetime.datetime
    id: strawberry.ID
    name: Optional[str] = None
    name_en: Optional[str] = None
    order: Optional[int] = None

@strawberry.type
class QuestionValueResultGQLModel:
    id: strawberry.ID = None
    msg: str = None

    @strawberry.field(description="""Result of question operation""")
    async def question(self, info: strawberry.types.Info) -> Union[QuestionValueGQLModel, None]:
        result = await QuestionValueGQLModel.resolve_reference(info, self.id)
        return result

@strawberry.mutation(description="""Creates new question value for closed question""")
async def question_value_insert(self, info: strawberry.types.Info, question_value: QuestionValueInsertGQLModel) -> QuestionValueResultGQLModel:
    loader = getLoaders(info).questionvalues
    row = await loader.insert(question_value)
    result = QuestionValueResultGQLModel()
    result.msg = "ok"
    result.id = row.id
    return result

@strawberry.mutation(description="""Updates question value / possible answer""")
async def question_value_update(self, info: strawberry.types.Info, question_value: QuestionValueUpdateGQLModel) -> QuestionValueResultGQLModel:
    loader = getLoaders(info).questionvalues
    row = await loader.update(question_value)
    result = QuestionValueResultGQLModel()
    result.msg = "ok"
    result.id = question_value.id
    if row is None:
        result.msg = "fail"           
    return result

@strawberry.mutation(description="""Updates question value / possible answer""")
async def question_value_delete(self, info: strawberry.types.Info, question_value_id: strawberry.ID) -> QuestionResultGQLModel:
    loader = getLoaders(info).questionvalues
    row = await loader.load(question_value_id)
    await loader.delete(question_value_id)
    result = QuestionResultGQLModel()
    result.msg = "ok"
    result.id = row.id
    if row is None:
        result.msg = "fail"           
    return result

