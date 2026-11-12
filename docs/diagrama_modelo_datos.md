# Diagrama entidad-relación – INTELLIGENT HOTEL

Este diagrama representa las entidades y relaciones definidas en los modelos Django del sistema de gestión operativa hotelera.

```mermaid
erDiagram
    HOTEL {
        int id PK
        string name
        string category
        string tax_id
        string city
        boolean is_active
    }

    OPERATIONAL_AREA {
        int id PK
        int hotel_id FK
        string code
        string name
        string area_type
    }

    APP_USER {
        int id PK
        int hotel_id FK
        string email
        string role
        boolean is_active
    }

    POSITION {
        int id PK
        string name
        boolean is_active
    }

    EMPLOYEE {
        int id PK
        int hotel_id FK
        int user_id FK
        int position_id FK
        int area_id FK
        string employee_code
        string document_number
        string employment_status
    }

    SHIFT {
        int id PK
        string name
        time start_time
        time end_time
    }

    EMPLOYEE_SHIFT {
        int id PK
        int employee_id FK
        int shift_id FK
        date work_date
        datetime start_datetime
        datetime end_datetime
        string status
    }

    EVENT_SPACE {
        int id PK
        int hotel_id FK
        string name
        int capacity
        boolean is_active
    }

    EVENT {
        int id PK
        int hotel_id FK
        int space_id FK
        int created_by_id FK
        string code
        string title
        datetime start_datetime
        datetime end_datetime
        string status
    }

    EVENT_STAFF_ASSIGNMENT {
        int id PK
        int event_id FK
        int employee_id FK
        int assigned_by_id FK
        string assigned_role
        datetime start_datetime
        datetime end_datetime
        string status
    }

    SERVICE_TYPE {
        int id PK
        int hotel_id FK
        int area_id FK
        string code
        string name
        string category
        int target_minutes
    }

    SERVICE_REQUEST {
        int id PK
        int hotel_id FK
        int service_type_id FK
        int assigned_area_id FK
        int assigned_employee_id FK
        int created_by_id FK
        int updated_by_id FK
        string request_code
        string guest_name
        string priority
        string status
    }

    REQUEST_HISTORY {
        int id PK
        int request_id FK
        int changed_by_id FK
        string previous_status
        string new_status
        datetime changed_at
    }

    OPERATIONAL_TASK {
        int id PK
        int hotel_id FK
        int area_id FK
        int service_request_id FK
        int event_id FK
        int assigned_employee_id FK
        int created_by_id FK
        string code
        string title
        string priority
        string status
    }

    INCIDENT {
        int id PK
        int hotel_id FK
        int area_id FK
        int service_request_id FK
        int event_id FK
        int employee_id FK
        int reported_by_id FK
        string code
        string title
        string severity
        string status
    }

    HOTEL ||--o{ OPERATIONAL_AREA : contiene
    HOTEL o|--o{ APP_USER : asigna
    HOTEL ||--o{ EMPLOYEE : emplea
    HOTEL ||--o{ EVENT_SPACE : dispone
    HOTEL ||--o{ EVENT : organiza
    HOTEL ||--o{ SERVICE_TYPE : define
    HOTEL ||--o{ SERVICE_REQUEST : recibe
    HOTEL ||--o{ OPERATIONAL_TASK : gestiona
    HOTEL ||--o{ INCIDENT : registra

    APP_USER o|--o| EMPLOYEE : tiene_perfil
    POSITION ||--o{ EMPLOYEE : clasifica
    OPERATIONAL_AREA ||--o{ EMPLOYEE : integra

    EMPLOYEE ||--o{ EMPLOYEE_SHIFT : tiene
    SHIFT ||--o{ EMPLOYEE_SHIFT : programa

    EVENT_SPACE ||--o{ EVENT : aloja
    APP_USER o|--o{ EVENT : crea
    EVENT ||--o{ EVENT_STAFF_ASSIGNMENT : requiere
    EMPLOYEE ||--o{ EVENT_STAFF_ASSIGNMENT : participa
    APP_USER o|--o{ EVENT_STAFF_ASSIGNMENT : asigna

    OPERATIONAL_AREA ||--o{ SERVICE_TYPE : ofrece
    SERVICE_TYPE ||--o{ SERVICE_REQUEST : clasifica
    OPERATIONAL_AREA ||--o{ SERVICE_REQUEST : atiende
    EMPLOYEE o|--o{ SERVICE_REQUEST : atiende
    APP_USER o|--o{ SERVICE_REQUEST : registra
    APP_USER o|--o{ SERVICE_REQUEST : actualiza
    SERVICE_REQUEST ||--o{ REQUEST_HISTORY : conserva
    APP_USER o|--o{ REQUEST_HISTORY : modifica

    OPERATIONAL_AREA ||--o{ OPERATIONAL_TASK : agrupa
    SERVICE_REQUEST o|--o{ OPERATIONAL_TASK : origina
    EVENT o|--o{ OPERATIONAL_TASK : genera
    EMPLOYEE o|--o{ OPERATIONAL_TASK : ejecuta
    APP_USER o|--o{ OPERATIONAL_TASK : crea

    OPERATIONAL_AREA ||--o{ INCIDENT : registra
    SERVICE_REQUEST o|--o{ INCIDENT : relaciona
    EVENT o|--o{ INCIDENT : relaciona
    EMPLOYEE o|--o{ INCIDENT : involucra
    APP_USER o|--o{ INCIDENT : reporta
