from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from config.database import get_db
from models.models import SystemPrompt, User
from schemas.system_prompt import SystemPromptCreate, SystemPromptUpdate, SystemPromptResponse
from auth.auth_utils import get_current_active_user, get_current_admin_user

router = APIRouter()

@router.post("/", response_model=SystemPromptResponse, status_code=status.HTTP_201_CREATED)
async def create_system_prompt(
    system_prompt: SystemPromptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new system prompt (admin only)
    """
    # Check if a prompt with this name already exists
    existing_prompt = db.query(SystemPrompt).filter(
        SystemPrompt.name == system_prompt.name
    ).first()
    
    if existing_prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"System prompt with name '{system_prompt.name}' already exists"
        )
    
    # Create new system prompt
    db_system_prompt = SystemPrompt(
        name=system_prompt.name,
        content=system_prompt.content,
        is_active=system_prompt.is_active,
        user_id=current_user.id
    )
    
    # If this is set as active, deactivate all other prompts
    if system_prompt.is_active:
        db.query(SystemPrompt).filter(
            SystemPrompt.id != db_system_prompt.id
        ).update({SystemPrompt.is_active: False})
    
    db.add(db_system_prompt)
    db.commit()
    db.refresh(db_system_prompt)
    
    return db_system_prompt

@router.get("/", response_model=List[SystemPromptResponse])
async def read_system_prompts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all system prompts
    """
    system_prompts = db.query(SystemPrompt).offset(skip).limit(limit).all()
    return system_prompts

@router.get("/active", response_model=SystemPromptResponse)
async def read_active_system_prompt(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the currently active system prompt
    """
    system_prompt = db.query(SystemPrompt).filter(SystemPrompt.is_active == True).first()
    if system_prompt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active system prompt found"
        )
    return system_prompt

@router.get("/{prompt_id}", response_model=SystemPromptResponse)
async def read_system_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get system prompt by ID
    """
    system_prompt = db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()
    if system_prompt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"System prompt with ID {prompt_id} not found"
        )
    return system_prompt

@router.put("/{prompt_id}", response_model=SystemPromptResponse)
async def update_system_prompt(
    prompt_id: int,
    system_prompt_update: SystemPromptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update system prompt by ID (admin only)
    """
    system_prompt = db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()
    if system_prompt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"System prompt with ID {prompt_id} not found"
        )
    
    # Update fields if provided
    if system_prompt_update.name is not None:
        # Check if new name already exists
        if system_prompt_update.name != system_prompt.name:
            existing_prompt = db.query(SystemPrompt).filter(
                SystemPrompt.name == system_prompt_update.name
            ).first()
            if existing_prompt:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"System prompt with name '{system_prompt_update.name}' already exists"
                )
        system_prompt.name = system_prompt_update.name
    
    if system_prompt_update.content is not None:
        system_prompt.content = system_prompt_update.content
    
    if system_prompt_update.is_active is not None:
        # If setting to active, deactivate all other prompts
        if system_prompt_update.is_active and not system_prompt.is_active:
            db.query(SystemPrompt).filter(
                SystemPrompt.id != prompt_id
            ).update({SystemPrompt.is_active: False})
        system_prompt.is_active = system_prompt_update.is_active
    
    db.commit()
    db.refresh(system_prompt)
    
    return system_prompt

@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_system_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete system prompt by ID (admin only)
    """
    system_prompt = db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()
    if system_prompt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"System prompt with ID {prompt_id} not found"
        )
    
    # Don't allow deleting the active prompt
    if system_prompt.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the active system prompt. Set another prompt as active first."
        )
    
    db.delete(system_prompt)
    db.commit()
    
    return None
