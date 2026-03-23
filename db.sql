create table projects
(
    id             varchar(255)                          not null
        primary key,
    owner          varchar(255)                          not null,
    name           varchar(500)                          null,
    script_title   varchar(500)                          null,
    episode_no     int         default 1                 null,
    video_provider varchar(50) default 'openai'          null,
    payload_json   longtext                              not null,
    created_at     datetime    default CURRENT_TIMESTAMP null,
    updated_at     datetime    default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP
)
    collate = utf8mb4_unicode_ci;

create table assets
(
    id         varchar(255)                       not null
        primary key,
    project_id varchar(255)                       not null,
    image_url  longtext                           null,
    name       varchar(500)                       null,
    prompt     longtext                           null,
    type       varchar(100)                       null,
    created_at datetime default CURRENT_TIMESTAMP null,
    constraint assets_ibfk_1
        foreign key (project_id) references projects (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create index idx_project_id
    on assets (project_id);

create table episode_scripts
(
    id              int auto_increment
        primary key,
    project_id      varchar(255)                       not null,
    episode_key     varchar(255)                       null,
    script_input    longtext                           null,
    script_duration varchar(50)                        null,
    script_result   json                               null,
    history         json                               null,
    created_at      datetime default CURRENT_TIMESTAMP null,
    constraint unique_project_episode
        unique (project_id, episode_key),
    constraint episode_scripts_ibfk_1
        foreign key (project_id) references projects (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create index idx_project_id
    on episode_scripts (project_id);

create table project_generated_data
(
    id             int auto_increment
        primary key,
    project_id     varchar(255)                       not null,
    generated_data json                               null,
    created_at     datetime default CURRENT_TIMESTAMP null,
    constraint project_generated_data_ibfk_1
        foreign key (project_id) references projects (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create index idx_project_id
    on project_generated_data (project_id);

create table project_history
(
    id           int auto_increment
        primary key,
    project_id   varchar(255)                       not null,
    history_data json                               null,
    created_at   datetime default CURRENT_TIMESTAMP null,
    constraint project_history_ibfk_1
        foreign key (project_id) references projects (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create index idx_project_id
    on project_history (project_id);

create table project_script
(
    project_id      varchar(255)                       not null
        primary key,
    script_input    longtext                           null,
    script_duration varchar(50)                        null,
    script_result   json                               null,
    created_at      datetime default CURRENT_TIMESTAMP null,
    updated_at      datetime default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP,
    constraint project_script_ibfk_1
        foreign key (project_id) references projects (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create index idx_owner
    on projects (owner);

create index idx_updated_at
    on projects (updated_at);

create table shots
(
    id                          int auto_increment
        primary key,
    project_id                  varchar(255)                       not null,
    scene_no                    int                                null,
    title                       varchar(500)                       null,
    duration                    varchar(50)                        null,
    dialogue_details            longtext                           null,
    bound_character_asset_ids   json                               null,
    bound_character_names       json                               null,
    start_frame_description     longtext                           null,
    start_frame_enhanced_prompt longtext                           null,
    start_frame_image_url       longtext                           null,
    end_frame_description       longtext                           null,
    end_frame_enhanced_prompt   longtext                           null,
    end_frame_image_url         longtext                           null,
    video_url                   longtext                           null,
    video_task_id               varchar(255)                       null,
    video_task_status           varchar(50)                        null,
    video_task_message          varchar(500)                       null,
    video_task_progress         int                                null,
    video_task_provider         varchar(50)                        null,
    created_at                  datetime default CURRENT_TIMESTAMP null,
    constraint shots_ibfk_1
        foreign key (project_id) references projects (id)
            on delete cascade
)
    collate = utf8mb4_unicode_ci;

create index idx_project_id
    on shots (project_id);

create table users
(
    username      varchar(255) not null
        primary key,
    password_hash varchar(255) not null,
    created_at    varchar(64)  not null,
    updated_at    varchar(64)  not null,
    last_login_at varchar(64)  null
)
    collate = utf8mb4_unicode_ci;

create index idx_users_updated_at
    on users (updated_at);

