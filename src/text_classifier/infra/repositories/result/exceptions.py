class ResultRepoError(Exception):
    pass

class DuplicatedResultError(ResultRepoError):
    pass

class ResultNotFoundError(ResultRepoError):
    pass
