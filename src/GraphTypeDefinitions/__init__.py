from typing import List, Union
import strawberry
from contextlib import asynccontextmanager

@strawberry.type(description="""Type for query root""")
class Query:
    from .Others import (
        survey_type_by_id, 
        survey_type_page,

        survey_by_id, 
        survey_page,

        answer_page,
        answer_by_id,

        question_by_id,
        question_page,

        question_type_by_id,
        question_type_page
    )

    answer_page = answer_page
    answer_by_id = answer_by_id

    survey_type_by_id = survey_type_by_id
    survey_type_page = survey_type_page

    survey_by_id = survey_by_id
    survey_page = survey_page

    question_by_id = question_by_id
    question_page = question_page

    question_type_by_id = question_type_by_id
    question_type_page = question_type_page
    pass

@strawberry.type(description="""Type for mutation root""")
class Mutation:
    from .Others import (
        survey_insert,
        survey_update,

        survey_type_insert,
        survey_type_update,

        question_insert,
        question_update,

        question_type_insert,
        question_type_update,

        answer_update,
        answer_insert
    )
    survey_insert = survey_insert
    survey_update = survey_update

    survey_type_insert = survey_type_insert
    survey_type_update = survey_type_update

    question_insert = question_insert
    question_update = question_update

    question_type_insert = question_type_insert
    question_type_update = question_type_update

    answer_update = answer_update
    answer_insert = answer_insert
    
    pass

schema = strawberry.federation.Schema(Query, mutation=Mutation)
