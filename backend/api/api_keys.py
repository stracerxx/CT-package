from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from config.database import get_db
from models.models import ApiKey, User
from schemas.api_keys import ApiKeyCreate, ApiKeyUpdate, ApiKeyResponse
from auth.auth_utils import get_current_active_user, get_current_admin_user

router = APIRouter()

@router.post("/", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key: ApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new API key (admin only)
    """
    # Check if service already has an active key
    existing_key = db.query(ApiKey).filter(
        ApiKey.service == api_key.service,
        ApiKey.is_active == True
    ).first()
    
    if existing_key:
        # Update existing key instead of creating a new one
        existing_key.api_key = api_key.api_key
        db.commit()
        db.refresh(existing_key)
        return existing_key
    
    # Create new API key
    db_api_key = ApiKey(
        service=api_key.service,
        api_key=api_key.api_key,
        is_active=api_key.is_active,
        user_id=current_user.id
    )
    
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    
    return db_api_key

@router.get("/", response_model=List[ApiKeyResponse])
async def read_api_keys(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get all API keys (admin only)
    """
    api_keys = db.query(ApiKey).offset(skip).limit(limit).all()
    return api_keys

@router.get("/{service}", response_model=ApiKeyResponse)
async def read_api_key(
    service: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get API key by service name (admin only)
    """
    api_key = db.query(ApiKey).filter(ApiKey.service == service).first()
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key for service '{service}' not found"
        )
    return api_key

@router.put("/{service}", response_model=ApiKeyResponse)
async def update_api_key(
    service: str,
    api_key_update: ApiKeyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update API key by service name (admin only)
    """
    api_key = db.query(ApiKey).filter(ApiKey.service == service).first()
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key for service '{service}' not found"
        )
    
    # Update fields if provided
    if api_key_update.api_key is not None:
        api_key.api_key = api_key_update.api_key
    if api_key_update.is_active is not None:
        api_key.is_active = api_key_update.is_active
    if api_key_update.service is not None and api_key_update.service != service:
        # Check if new service name already exists
        existing_key = db.query(ApiKey).filter(ApiKey.service == api_key_update.service).first()
        if existing_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"API key for service '{api_key_update.service}' already exists"
            )
        api_key.service = api_key_update.service
    
    db.commit()
    db.refresh(api_key)
    
    return api_key

@router.delete("/{service}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    service: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete API key by service name (admin only)
    """
    api_key = db.query(ApiKey).filter(ApiKey.service == service).first()
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key for service '{service}' not found"
        )
    
    db.delete(api_key)
    db.commit()
    
    return None
