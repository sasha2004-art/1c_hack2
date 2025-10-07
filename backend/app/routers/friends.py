from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas, models
from ..dependencies import get_current_active_user
from ..db.base import get_db

router = APIRouter(
    prefix="/friends",
    tags=["friends"]
)

@router.get("/", response_model=schemas.FriendsAndRequestsResponse)
def get_my_friends_and_requests(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Получить списки друзей, входящих и исходящих заявок."""
    all_friendships = crud.get_all_user_friendships(db, user_id=current_user.id)
    
    response = schemas.FriendsAndRequestsResponse()

    for fs in all_friendships:
        if fs.status == models.FriendshipStatus.ACCEPTED:
            # Определяем, кто в этой паре является другом
            if fs.requester_id == current_user.id:
                friend_details = fs.addressee
            else:
                friend_details = fs.requester
            
            response.friends.append(schemas.FriendRead(
                friendship_id=fs.id,
                friend_details=schemas.UserInComment.from_orm(friend_details)
            ))

        elif fs.status == models.FriendshipStatus.PENDING:
            if fs.addressee_id == current_user.id: # Если заявка адресована мне
                response.incoming_requests.append(schemas.IncomingRequestRead.from_orm(fs))
            else: # Если я отправил заявку
                response.outgoing_requests.append(schemas.OutgoingRequestRead.from_orm(fs))
                
    return response

@router.post("/request/{addressee_id}", status_code=status.HTTP_201_CREATED)
def send_friend_request(
    addressee_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Отправить заявку в друзья пользователю по его ID."""
    if addressee_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot send a friend request to yourself.")
    
    addressee = crud.get_user(db, user_id=addressee_id)
    if not addressee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        
    existing_friendship = crud.get_existing_friendship(db, user1_id=current_user.id, user2_id=addressee_id)
    if existing_friendship:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A friendship or request already exists between you and this user.")
        
    crud.create_friend_request(db, requester_id=current_user.id, addressee_id=addressee_id)
    return {"message": "Friend request sent."}

@router.post("/accept/{request_id}", status_code=status.HTTP_200_OK)
def accept_friend_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Принять входящую заявку в друзья."""
    db_request = crud.get_friendship_request(db, request_id=request_id)
    
    if not db_request or db_request.status != models.FriendshipStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pending request not found.")
        
    if db_request.addressee_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only accept requests addressed to you.")
        
    crud.update_friendship_status(db, db_friendship=db_request, status=models.FriendshipStatus.ACCEPTED)
    return {"message": "Friend request accepted."}
    
@router.post("/decline/{request_id}", status_code=status.HTTP_200_OK)
def decline_friend_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Отклонить входящую заявку в друзья (запись будет удалена)."""
    db_request = crud.get_friendship_request(db, request_id=request_id)
    
    if not db_request or db_request.status != models.FriendshipStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pending request not found.")
        
    if db_request.addressee_id != current_user.id and db_request.requester_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot decline this request.")
        
    crud.delete_friendship(db, db_friendship=db_request)
    return {"message": "Friend request declined."}

@router.delete("/{friendship_id}", status_code=status.HTTP_200_OK)
def remove_friend(
    friendship_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Удалить пользователя из друзей (или отменить исходящую заявку)."""
    db_friendship = crud.get_friendship_request(db, request_id=friendship_id)
    
    if not db_friendship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friendship not found.")
        
    if db_friendship.requester_id != current_user.id and db_friendship.addressee_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not part of this friendship.")
        
    crud.delete_friendship(db, db_friendship=db_friendship)
    return {"message": "Friend removed successfully."}