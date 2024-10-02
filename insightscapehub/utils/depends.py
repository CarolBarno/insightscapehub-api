from insightscapehub.utils.db import Session
from sqlalchemy import select, func, and_, desc, asc
from fastapi import HTTPException, status
from fastapi import Query
import math


def create_update_delete(model, db: Session, data: any, method='create', query=None, schema=None):

    response = None
    record = None

    try:
        if query:
            stmt = select(model)
            for key, value in query.items():
                stmt = stmt.filter(getattr(model, key) == value)
            record = db.execute(stmt).scalars().first()

        if method == 'create':

            if record:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail='Record already found')
            record = model(**data.dict())
            db.add(record)
            db.commit()
            response = schema.model_validate(record) if schema else record

        if method == 'update':

            if not record:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail='Record not found')
            for key, value in data.dict().items():
                if value is not None:
                    setattr(record, key, value)
            db.commit()
            db.refresh(record)
            response = schema.model_validate(record) if schema else record

        if method == 'delete':
            if not record:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail='Record not found')
            record.status = 'DELETED'
            db.commit()
            db.refresh(record)

        return response
    except Exception as e:
        raise e


def extract_pagination_params(
        page: int = Query(default=1, title='Page number',
                          description='Page number for pagination'),
        limit: int = Query(default=10, title='Page limit',
                           description='Number of items per page', enum=[10, 20])
) -> dict:

    pagination_params = {}

    if page is not None:
        pagination_params['page'] = page

    if limit is not None:
        pagination_params['limit'] = limit

    return pagination_params


def get_records(model, db: Session, query: dict = {}, condition: dict = {}, schema: any = None):
    """
    Retrieve records
    Arguments:
    model
    db (Session): database session object
    query (optional): dictionay containing query parameters, example, 'page', 'limit', 'order_by'
    condition (optional)
    schema (optional)
    Returns: dict - containing retrieved records
    Raises: Exception - any exception that occur during database query execution

    Example:
    models = [{'model': Model, 'conditions': Model.id == 'id'}]
    query_params = {'page': 1, 'limit': 10, 'order_by': [('column_name', 'ASC')]}
    result = get_records(models, db_session, query=query_params, schema=my_schema)
    """

    try:
        models = model

        if not isinstance(models, list):
            models = [
                {
                    'model': model,
                    'conditions': condition
                }
            ]

        if 'page' in query:
            page = int(query['page'])
            limit = int(query.get('limit', 10))
            offset = (page - 1) * limit

            stmt = select(models[0]['model']).limit(limit).offset(offset)

            for join in models[1:]:
                model = join['model']
                conditions = join.get('conditions', None)
                stmt = stmt.join(model, conditions)

            if condition:
                filter = []
                for key, value in condition.items():
                    if '.' in key:
                        json_key, sub_key = key.split('.', 1)
                        json_column = getattr(models[0]['model'], json_key)
                        filter.append(func.json_extract_path_text(
                            json_column, *sub_key.split('.')) == value)
                    else:
                        if isinstance(value, list):
                            filter.append(
                                getattr(models[0]['model'], key).in_(value))
                        else:
                            filter.append(
                                getattr(models[0]['model'], key) == value)

                stmt = stmt.filter(and_(*filter))

            count_stmt = select(func.count().label(
                'total')).select_from(models[0]['model'])

            if condition:
                filter_count = []
                for key, value in condition.items():
                    if '.' in key:
                        json_key, sub_key = key.split('.', 1)
                        json_column = getattr(models[0]['model'], json_key)
                        filter_count.append(func.json_extract_path_text(
                            json_column, *sub_key.split('.')) == value)
                    else:
                        if isinstance(value, list):
                            filter_count.append(
                                getattr(models[0]['model'], key).in_(value))
                        else:
                            filter_count.append(
                                getattr(models[0]['model'], key) == value)

                count_stmt = count_stmt.filter(and_(*filter_count))

            if 'order_by' in query and query['order_by']:
                order_by_list = []
                for order_by_column, order_direction in query['order_by']:
                    column = getattr(models[0]['model'], order_by_column)
                    if order_direction.lower == 'desc':
                        order_by_list.append(desc(column))
                    else:
                        order_by_list.append(asc(column))

                stmt = stmt.order_by(*order_by_list)

            records = db.execute(stmt).scalars().all()
            total_count = db.execute(count_stmt).scalar()
            total_pages = math.ceil(total_count / query['limit']) or 1
            results = [schema.model_validate(
                record) for record in records] if schema else records

            data = {
                'page_info': {
                    'page': query['page'],
                    'has_next': True if query['page'] < total_pages else False,
                    'has_previous': False if query['page'] == 1 else True,
                    'page_count': len(results),
                    'total_count': total_count,
                    'total_pages': total_pages
                },
                'results': results
            }
        else:
            stmt = select(models[0]['model'])

            for join in models[1:]:
                model = join['model']
                conditions = join.get('conditions', None)
                stmt = stmt.join(model, conditions)

            if condition:
                filter = []
                for key, value in condition.items():
                    if isinstance(value, list):
                        filter.append(
                            getattr(models[0]['model'], key).in_(value))
                    else:
                        filter.append(
                            getattr(models[0]['model'], key) == value)

                stmt = stmt.filter(and_(*filter))

            data = db.execute(stmt).scalars().all()

            if schema and data:
                data = [schema.model_validate(record) for record in data]

        return data
    except Exception as e:
        raise e
