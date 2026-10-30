with open('backend/app/api/users/routes.py', 'r', encoding='utf-8') as f:
    code = f.read()

if "/onboarding/selections" not in code:
    import_target = "from app.schemas.onboarding import ("
    import_replacement = "from app.schemas.onboarding import (\n    OnboardingSelectionsResponse,"
    assert import_target in code, "import_target not found"
    code = code.replace(import_target, import_replacement, 1)

    new_endpoint = """

@router.get(
    "/onboarding/selections",
    response_model=OnboardingSelectionsResponse,
    summary="Get unified current student onboarding selections",
)
def get_onboarding_selections(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> OnboardingSelectionsResponse:
    \"\"\"Retrieve the single source of truth for the student's active onboarding choices.\"\"\"
    try:
        return OnboardingService.get_current_selections(
            db=db, user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
"""
    code = code.rstrip() + new_endpoint
    with open('backend/app/api/users/routes.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Added /onboarding/selections to routes.py")
else:
    print("/onboarding/selections already in routes.py")

