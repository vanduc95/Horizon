import services

first_service = services.db_session.query(services.Service).first()
print(first_service.id)