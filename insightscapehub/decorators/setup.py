from typing import Callable, Iterable, List, Union
from fastapi import APIRouter, Depends


_auth_dependencies = []


def _is_unauthenticated_route(endpoint: Callable):
    return hasattr(endpoint, 'unauthenticated')


def _is_authenticated_route(endpoint: Callable):
    return hasattr(endpoint, 'authenticated')


def _is_auth_dependency(dependency: Depends) -> bool:
    name = dependency.dependency.__name__
    return name in _auth_dependencies


def _remove_auth_dependencies(dependencies: Union[None, List[Depends]]):
    if not dependencies:
        return []

    return [dep for dep in dependencies if not _is_auth_dependency(dep)]


def _add_auth_dependencies(dependencies: Union[None, list[Depends]]):
    if not dependencies:
        dependencies = []

    deps = [dep for dep in dependencies if _is_auth_dependency(dep)]

    # if len(deps) == 0:
    #     dependencies.append(Depends())

    return dependencies


def initialize_routers(routers: Iterable[APIRouter]):
    for router in routers:
        for route in router.routes:
            is_unauth = _is_unauthenticated_route(route.endpoint)

            if is_unauth:
                route.dependencies = _remove_auth_dependencies(
                    route.dependencies)
            else:
                is_auth = _is_authenticated_route(route.endpoint)
                if is_auth:
                    route.dependencies = _add_auth_dependencies(
                        route.dependencies)

    return routers
