from fastapi import HTTPException, status


# User
UserNotExistsException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not exists",
)

UserNotAuthorizeException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="User is not authorized",
)

UserAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="User already exists",
)

NoAccessRightsException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You don't have access rights",
)

EmailOrPasswordIncorrectException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Email or password incorrect",
)


# Token
TokenExpiredException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token expired",
)

TokenNotFoundException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token not found",
)

IncorrectTokenFormatException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect token format",
)


# Task
TaskNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Task not found"
)

TaskWasNotUpdatedException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Task was not updated"
)

TaskAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Task with this title already exists"
)

TaskCreationFailedException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Failed to create task"
)
