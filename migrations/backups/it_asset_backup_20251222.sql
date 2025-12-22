--
-- PostgreSQL database dump
--

\restrict QmBRqfimiD1UHwk4oftMij722r1nQpvjY3eiRYt1UwOyBo9h58JLPDVr7ZyH8s9

-- Dumped from database version 14.20 (Debian 14.20-1.pgdg13+1)
-- Dumped by pg_dump version 14.20 (Debian 14.20-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: account_request; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.account_request (
    id integer NOT NULL,
    username character varying(64),
    full_name character varying(120),
    employee_no character varying(64),
    email character varying(120),
    department character varying(120),
    role_requested character varying(64),
    reason text,
    password_hash character varying(128),
    status character varying(32),
    created_date timestamp without time zone,
    processed_date timestamp without time zone,
    approver_id integer,
    approver_comments text
);


ALTER TABLE public.account_request OWNER TO postgres;

--
-- Name: account_request_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.account_request_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.account_request_id_seq OWNER TO postgres;

--
-- Name: account_request_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.account_request_id_seq OWNED BY public.account_request.id;


--
-- Name: action_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.action_log (
    id integer NOT NULL,
    action_name character varying(120),
    workflow_node_id integer,
    approval_workflow_id integer,
    payload text,
    status character varying(32),
    result text,
    executed_at timestamp without time zone,
    retry_count integer
);


ALTER TABLE public.action_log OWNER TO postgres;

--
-- Name: action_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.action_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.action_log_id_seq OWNER TO postgres;

--
-- Name: action_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.action_log_id_seq OWNED BY public.action_log.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(255) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: announcement_attachment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.announcement_attachment (
    id integer NOT NULL,
    announcement_id integer NOT NULL,
    filename character varying(255) NOT NULL,
    stored_filename character varying(255) NOT NULL,
    file_path character varying(512) NOT NULL,
    file_size integer NOT NULL,
    file_type character varying(128),
    thumbnail_path character varying(512),
    upload_user_id integer NOT NULL,
    created_date timestamp without time zone,
    is_deleted boolean,
    deleted_date timestamp without time zone
);


ALTER TABLE public.announcement_attachment OWNER TO postgres;

--
-- Name: announcement_attachment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.announcement_attachment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.announcement_attachment_id_seq OWNER TO postgres;

--
-- Name: announcement_attachment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.announcement_attachment_id_seq OWNED BY public.announcement_attachment.id;


--
-- Name: announcements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.announcements (
    id integer NOT NULL,
    title character varying(200) NOT NULL,
    content text NOT NULL,
    type character varying(20) NOT NULL,
    priority character varying(20) NOT NULL,
    is_pinned boolean,
    is_published boolean,
    publish_time timestamp without time zone,
    expire_time timestamp without time zone,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    creator_id integer NOT NULL
);


ALTER TABLE public.announcements OWNER TO postgres;

--
-- Name: COLUMN announcements.title; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.announcements.title IS '公告标题';


--
-- Name: COLUMN announcements.content; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.announcements.content IS '公告内容';


--
-- Name: COLUMN announcements.type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.announcements.type IS '公告类型';


--
-- Name: COLUMN announcements.priority; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.announcements.priority IS '优先级';


--
-- Name: COLUMN announcements.is_pinned; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.announcements.is_pinned IS '是否置顶';


--
-- Name: COLUMN announcements.is_published; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.announcements.is_published IS '是否发布';


--
-- Name: COLUMN announcements.publish_time; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.announcements.publish_time IS '发布时间';


--
-- Name: COLUMN announcements.expire_time; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.announcements.expire_time IS '过期时间';


--
-- Name: COLUMN announcements.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.announcements.created_at IS '创建时间';


--
-- Name: COLUMN announcements.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.announcements.updated_at IS '更新时间';


--
-- Name: COLUMN announcements.creator_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.announcements.creator_id IS '创建者ID';


--
-- Name: announcements_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.announcements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.announcements_id_seq OWNER TO postgres;

--
-- Name: announcements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.announcements_id_seq OWNED BY public.announcements.id;


--
-- Name: announcements_publish_time_backup; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.announcements_publish_time_backup (
    id integer NOT NULL,
    publish_time timestamp without time zone,
    created_at timestamp without time zone,
    backed_up_at timestamp without time zone
);


ALTER TABLE public.announcements_publish_time_backup OWNER TO postgres;

--
-- Name: app_user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.app_user (
    id integer NOT NULL,
    username character varying(64),
    email character varying(120),
    password_hash character varying(256),
    role character varying(64),
    department_id integer,
    department character varying(120),
    is_active boolean,
    workflow_roles text,
    can_manage_equipment boolean,
    can_manage_spare_parts boolean,
    can_manage_repairs boolean,
    can_manage_part_requests boolean,
    can_view_workflow boolean,
    can_edit_workflow boolean,
    can_manage_workflow_templates boolean,
    can_view_reports boolean,
    can_view_logs boolean
);


ALTER TABLE public.app_user OWNER TO postgres;

--
-- Name: app_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.app_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.app_user_id_seq OWNER TO postgres;

--
-- Name: app_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.app_user_id_seq OWNED BY public.app_user.id;


--
-- Name: approval_decision; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.approval_decision (
    id integer NOT NULL,
    approval_workflow_id integer,
    approver_id integer,
    decision character varying(32),
    comments text,
    created_at timestamp without time zone
);


ALTER TABLE public.approval_decision OWNER TO postgres;

--
-- Name: approval_decision_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.approval_decision_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.approval_decision_id_seq OWNER TO postgres;

--
-- Name: approval_decision_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.approval_decision_id_seq OWNED BY public.approval_decision.id;


--
-- Name: approval_delegate; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.approval_delegate (
    id integer NOT NULL,
    user_id integer NOT NULL,
    delegate_to_id integer NOT NULL,
    order_types json,
    role_ids json,
    start_date timestamp without time zone NOT NULL,
    end_date timestamp without time zone NOT NULL,
    is_active boolean,
    reason text,
    created_date timestamp without time zone
);


ALTER TABLE public.approval_delegate OWNER TO postgres;

--
-- Name: approval_delegate_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.approval_delegate_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.approval_delegate_id_seq OWNER TO postgres;

--
-- Name: approval_delegate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.approval_delegate_id_seq OWNED BY public.approval_delegate.id;


--
-- Name: approval_instance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.approval_instance (
    id integer NOT NULL,
    instance_no character varying(64) NOT NULL,
    template_id integer NOT NULL,
    order_type character varying(64) NOT NULL,
    order_id integer NOT NULL,
    requester_id integer NOT NULL,
    requester_dept_id integer,
    status character varying(32),
    current_node_id integer,
    started_date timestamp without time zone,
    completed_date timestamp without time zone,
    expected_complete_date timestamp without time zone,
    form_data json,
    context_data json,
    final_result character varying(32),
    final_comment text
);


ALTER TABLE public.approval_instance OWNER TO postgres;

--
-- Name: approval_instance_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.approval_instance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.approval_instance_id_seq OWNER TO postgres;

--
-- Name: approval_instance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.approval_instance_id_seq OWNED BY public.approval_instance.id;


--
-- Name: approval_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.approval_log (
    id integer NOT NULL,
    instance_id integer,
    step_id integer,
    action character varying(64) NOT NULL,
    operator_id integer,
    operator_role character varying(64),
    old_value json,
    new_value json,
    comment text,
    ip_address character varying(64),
    user_agent character varying(512),
    created_date timestamp without time zone
);


ALTER TABLE public.approval_log OWNER TO postgres;

--
-- Name: approval_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.approval_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.approval_log_id_seq OWNER TO postgres;

--
-- Name: approval_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.approval_log_id_seq OWNED BY public.approval_log.id;


--
-- Name: approval_reminder; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.approval_reminder (
    id integer NOT NULL,
    step_id integer NOT NULL,
    reminder_type character varying(32),
    sent_to_id integer,
    sent_date timestamp without time zone,
    send_method character varying(32),
    is_sent boolean,
    sent_result text
);


ALTER TABLE public.approval_reminder OWNER TO postgres;

--
-- Name: approval_reminder_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.approval_reminder_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.approval_reminder_id_seq OWNER TO postgres;

--
-- Name: approval_reminder_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.approval_reminder_id_seq OWNED BY public.approval_reminder.id;


--
-- Name: approval_role; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.approval_role (
    id integer NOT NULL,
    code character varying(64) NOT NULL,
    name character varying(120) NOT NULL,
    description text,
    category character varying(64),
    level integer,
    icon character varying(64),
    color character varying(32),
    can_approve_repair boolean,
    can_approve_part_request boolean,
    can_approve_equipment_transfer boolean,
    can_approve_equipment_scrap boolean,
    can_approve_equipment_loan boolean,
    can_approve_equipment_application boolean,
    max_approval_amount double precision,
    is_active boolean,
    is_system_role boolean,
    created_date timestamp without time zone,
    updated_date timestamp without time zone,
    created_by_id integer
);


ALTER TABLE public.approval_role OWNER TO postgres;

--
-- Name: approval_role_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.approval_role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.approval_role_id_seq OWNER TO postgres;

--
-- Name: approval_role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.approval_role_id_seq OWNED BY public.approval_role.id;


--
-- Name: approval_step; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.approval_step (
    id integer NOT NULL,
    instance_id integer NOT NULL,
    node_id integer NOT NULL,
    sequence integer NOT NULL,
    step_no character varying(64),
    approver_id integer,
    approver_role_id integer,
    assigned_date timestamp without time zone,
    parallel_group_id character varying(64),
    parallel_approvers json,
    approved_count integer,
    status character varying(32),
    result character varying(32),
    comment text,
    approved_date timestamp without time zone,
    transferred_from_id integer,
    transferred_to_id integer,
    transfer_reason text,
    deadline timestamp without time zone,
    is_timeout boolean,
    timeout_handled_date timestamp without time zone,
    admin_action character varying(32),
    admin_operator_id integer,
    admin_comment text
);


ALTER TABLE public.approval_step OWNER TO postgres;

--
-- Name: approval_step_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.approval_step_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.approval_step_id_seq OWNER TO postgres;

--
-- Name: approval_step_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.approval_step_id_seq OWNED BY public.approval_step.id;


--
-- Name: approval_workflow; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.approval_workflow (
    id integer NOT NULL,
    order_type character varying(64),
    order_id integer,
    approver_id integer,
    approval_level character varying(64),
    node_id integer,
    status character varying(64),
    comments text,
    created_date timestamp without time zone,
    approved_date timestamp without time zone,
    auto_assigned boolean,
    action_type character varying(32),
    repair_cost_input double precision,
    transferred_from_id integer,
    admin_action character varying(32),
    admin_operator_id integer,
    required_approvals integer DEFAULT 1,
    actions_on_reject text
);


ALTER TABLE public.approval_workflow OWNER TO postgres;

--
-- Name: approval_workflow_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.approval_workflow_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.approval_workflow_id_seq OWNER TO postgres;

--
-- Name: approval_workflow_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.approval_workflow_id_seq OWNED BY public.approval_workflow.id;


--
-- Name: asset_cost; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.asset_cost (
    id integer NOT NULL,
    equipment_id integer,
    purchase_price double precision,
    purchase_date date,
    maintenance_cost double precision,
    depreciation_rate double precision,
    residual_value double precision,
    depreciation_method character varying(64),
    expected_lifespan integer,
    supplier character varying(120),
    warranty_period integer,
    created_date timestamp without time zone,
    updated_date timestamp without time zone
);


ALTER TABLE public.asset_cost OWNER TO postgres;

--
-- Name: asset_cost_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.asset_cost_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.asset_cost_id_seq OWNER TO postgres;

--
-- Name: asset_cost_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.asset_cost_id_seq OWNED BY public.asset_cost.id;


--
-- Name: asset_handover; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.asset_handover (
    id integer NOT NULL,
    from_user_id integer,
    to_user_id integer,
    equipment_ids text,
    status character varying(64),
    reason character varying(64),
    reason_detail text,
    created_date timestamp without time zone,
    completed_date timestamp without time zone,
    completed_by_id integer
);


ALTER TABLE public.asset_handover OWNER TO postgres;

--
-- Name: asset_handover_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.asset_handover_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.asset_handover_id_seq OWNER TO postgres;

--
-- Name: asset_handover_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.asset_handover_id_seq OWNED BY public.asset_handover.id;


--
-- Name: asset_lifecycle; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.asset_lifecycle (
    id integer NOT NULL,
    equipment_id integer,
    event_type character varying(64),
    event_date timestamp without time zone,
    old_status character varying(64),
    new_status character varying(64),
    description text,
    responsible_user_id integer,
    cost_involved double precision,
    documents text
);


ALTER TABLE public.asset_lifecycle OWNER TO postgres;

--
-- Name: asset_lifecycle_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.asset_lifecycle_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.asset_lifecycle_id_seq OWNER TO postgres;

--
-- Name: asset_lifecycle_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.asset_lifecycle_id_seq OWNED BY public.asset_lifecycle.id;


--
-- Name: audit_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_log (
    id integer NOT NULL,
    user_id integer,
    action_type character varying(64),
    resource_type character varying(64),
    resource_id integer,
    old_value text,
    new_value text,
    ip_address character varying(64),
    reason text,
    created_date timestamp without time zone
);


ALTER TABLE public.audit_log OWNER TO postgres;

--
-- Name: audit_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.audit_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.audit_log_id_seq OWNER TO postgres;

--
-- Name: audit_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.audit_log_id_seq OWNED BY public.audit_log.id;


--
-- Name: chat_attachment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_attachment (
    id integer NOT NULL,
    message_id integer,
    filename character varying(255) NOT NULL,
    stored_filename character varying(255) NOT NULL,
    file_path character varying(512) NOT NULL,
    file_size integer NOT NULL,
    file_type character varying(128),
    thumbnail_path character varying(512),
    created_date timestamp without time zone,
    upload_user_id integer
);


ALTER TABLE public.chat_attachment OWNER TO postgres;

--
-- Name: chat_attachment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.chat_attachment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.chat_attachment_id_seq OWNER TO postgres;

--
-- Name: chat_attachment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.chat_attachment_id_seq OWNED BY public.chat_attachment.id;


--
-- Name: chat_conversation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_conversation (
    id integer NOT NULL,
    conversation_type character varying(20) NOT NULL,
    name character varying(200),
    avatar_url character varying(512),
    description text,
    creator_id integer NOT NULL,
    is_active boolean,
    created_date timestamp without time zone,
    updated_date timestamp without time zone,
    last_message_id integer,
    last_message_time timestamp without time zone
);


ALTER TABLE public.chat_conversation OWNER TO postgres;

--
-- Name: chat_conversation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.chat_conversation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.chat_conversation_id_seq OWNER TO postgres;

--
-- Name: chat_conversation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.chat_conversation_id_seq OWNED BY public.chat_conversation.id;


--
-- Name: chat_message; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_message (
    id integer NOT NULL,
    conversation_id integer NOT NULL,
    sender_id integer NOT NULL,
    message_type character varying(20) NOT NULL,
    content text,
    is_recalled boolean,
    recalled_date timestamp without time zone,
    is_deleted boolean,
    created_date timestamp without time zone,
    reply_to_message_id integer
);


ALTER TABLE public.chat_message OWNER TO postgres;

--
-- Name: chat_message_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.chat_message_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.chat_message_id_seq OWNER TO postgres;

--
-- Name: chat_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.chat_message_id_seq OWNED BY public.chat_message.id;


--
-- Name: chat_participant; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_participant (
    id integer NOT NULL,
    conversation_id integer NOT NULL,
    user_id integer NOT NULL,
    joined_date timestamp without time zone,
    last_read_message_id integer,
    unread_count integer,
    is_pinned boolean,
    is_muted boolean,
    is_left boolean,
    left_date timestamp without time zone,
    role character varying(20)
);


ALTER TABLE public.chat_participant OWNER TO postgres;

--
-- Name: chat_participant_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.chat_participant_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.chat_participant_id_seq OWNER TO postgres;

--
-- Name: chat_participant_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.chat_participant_id_seq OWNED BY public.chat_participant.id;


--
-- Name: chat_permission; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_permission (
    id integer NOT NULL,
    user_id integer NOT NULL,
    can_send_message boolean,
    can_send_file boolean,
    can_create_group boolean,
    muted_until timestamp without time zone,
    notes text,
    operated_by_id integer,
    operated_date timestamp without time zone
);


ALTER TABLE public.chat_permission OWNER TO postgres;

--
-- Name: chat_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.chat_permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.chat_permission_id_seq OWNER TO postgres;

--
-- Name: chat_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.chat_permission_id_seq OWNED BY public.chat_permission.id;


--
-- Name: department; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.department (
    id integer NOT NULL,
    name character varying(120),
    code character varying(64),
    cost_center character varying(64),
    location character varying(120),
    description text
);


ALTER TABLE public.department OWNER TO postgres;

--
-- Name: department_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.department_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.department_id_seq OWNER TO postgres;

--
-- Name: department_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.department_id_seq OWNED BY public.department.id;


--
-- Name: equipment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipment (
    id integer NOT NULL,
    name character varying(120),
    type_id integer,
    type character varying(64),
    brand character varying(64),
    model character varying(64),
    serial_number character varying(120),
    equipment_number character varying(120),
    purchase_date date,
    price double precision,
    department_id integer,
    department character varying(120),
    location character varying(120),
    status character varying(64),
    is_public_pool boolean,
    require_return_inspection boolean,
    allow_loan boolean
);


ALTER TABLE public.equipment OWNER TO postgres;

--
-- Name: equipment_application; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipment_application (
    id integer NOT NULL,
    equipment_id integer,
    applicant_id integer,
    applicant_dept character varying(120),
    reason text,
    status character varying(64),
    created_date timestamp without time zone,
    approved_date timestamp without time zone
);


ALTER TABLE public.equipment_application OWNER TO postgres;

--
-- Name: equipment_application_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.equipment_application_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.equipment_application_id_seq OWNER TO postgres;

--
-- Name: equipment_application_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.equipment_application_id_seq OWNED BY public.equipment_application.id;


--
-- Name: equipment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.equipment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.equipment_id_seq OWNER TO postgres;

--
-- Name: equipment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.equipment_id_seq OWNED BY public.equipment.id;


--
-- Name: equipment_loan; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipment_loan (
    id integer NOT NULL,
    equipment_id integer,
    requester_id integer,
    requester_dept character varying(120),
    start_date timestamp without time zone,
    end_date timestamp without time zone,
    status character varying(64),
    approved_by integer,
    approved_date timestamp without time zone,
    borrowed_date timestamp without time zone,
    return_request_date timestamp without time zone,
    return_notes text,
    return_condition character varying(64),
    inspected_by integer,
    inspection_date timestamp without time zone,
    inspection_notes text,
    inspection_result character varying(64),
    damage_compensation double precision,
    damage_description text,
    returned_date timestamp without time zone,
    notes text,
    pickup_notified boolean,
    created_date timestamp without time zone,
    updated_date timestamp without time zone
);


ALTER TABLE public.equipment_loan OWNER TO postgres;

--
-- Name: equipment_loan_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.equipment_loan_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.equipment_loan_id_seq OWNER TO postgres;

--
-- Name: equipment_loan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.equipment_loan_id_seq OWNED BY public.equipment_loan.id;


--
-- Name: equipment_scrap; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipment_scrap (
    id integer NOT NULL,
    equipment_id integer,
    requester_id integer,
    description text,
    status character varying(64),
    created_date timestamp without time zone,
    updated_date timestamp without time zone,
    disposal_method character varying(64),
    disposal_date timestamp without time zone,
    disposal_handler integer,
    disposal_notes text,
    disposal_value double precision,
    disposal_company character varying(200),
    financial_cleared boolean,
    financial_cleared_date timestamp without time zone,
    financial_cleared_by integer,
    financial_notes text
);


ALTER TABLE public.equipment_scrap OWNER TO postgres;

--
-- Name: equipment_scrap_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.equipment_scrap_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.equipment_scrap_id_seq OWNER TO postgres;

--
-- Name: equipment_scrap_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.equipment_scrap_id_seq OWNED BY public.equipment_scrap.id;


--
-- Name: equipment_transfer; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipment_transfer (
    id integer NOT NULL,
    equipment_id integer,
    from_department character varying(120),
    to_department character varying(120),
    requester_id integer,
    description text,
    status character varying(64),
    created_date timestamp without time zone,
    updated_date timestamp without time zone
);


ALTER TABLE public.equipment_transfer OWNER TO postgres;

--
-- Name: equipment_transfer_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.equipment_transfer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.equipment_transfer_id_seq OWNER TO postgres;

--
-- Name: equipment_transfer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.equipment_transfer_id_seq OWNED BY public.equipment_transfer.id;


--
-- Name: equipment_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipment_type (
    id integer NOT NULL,
    name character varying(120) NOT NULL,
    description text,
    created_date timestamp without time zone
);


ALTER TABLE public.equipment_type OWNER TO postgres;

--
-- Name: equipment_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.equipment_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.equipment_type_id_seq OWNER TO postgres;

--
-- Name: equipment_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.equipment_type_id_seq OWNED BY public.equipment_type.id;


--
-- Name: inventory_warning; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.inventory_warning (
    id integer NOT NULL,
    spare_part_id integer,
    min_threshold integer,
    critical_threshold integer,
    reorder_quantity integer,
    lead_time_days integer,
    enabled boolean,
    last_warned_date timestamp without time zone,
    created_date timestamp without time zone
);


ALTER TABLE public.inventory_warning OWNER TO postgres;

--
-- Name: inventory_warning_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.inventory_warning_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.inventory_warning_id_seq OWNER TO postgres;

--
-- Name: inventory_warning_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inventory_warning_id_seq OWNED BY public.inventory_warning.id;


--
-- Name: maintenance_plan; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.maintenance_plan (
    id integer NOT NULL,
    equipment_id integer NOT NULL,
    plan_name character varying(200),
    maintenance_type character varying(64),
    interval_days integer,
    next_maintenance_date date,
    last_maintenance_date date,
    responsible_person integer,
    description text,
    is_active boolean,
    created_by integer,
    created_date timestamp without time zone,
    updated_date timestamp without time zone
);


ALTER TABLE public.maintenance_plan OWNER TO postgres;

--
-- Name: maintenance_plan_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.maintenance_plan_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.maintenance_plan_id_seq OWNER TO postgres;

--
-- Name: maintenance_plan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.maintenance_plan_id_seq OWNED BY public.maintenance_plan.id;


--
-- Name: maintenance_record; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.maintenance_record (
    id integer NOT NULL,
    plan_id integer,
    equipment_id integer NOT NULL,
    maintenance_date timestamp without time zone,
    maintenance_type character varying(64),
    performed_by integer,
    description text,
    notes text,
    cost double precision,
    next_maintenance_date date,
    status character varying(64),
    created_date timestamp without time zone
);


ALTER TABLE public.maintenance_record OWNER TO postgres;

--
-- Name: maintenance_record_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.maintenance_record_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.maintenance_record_id_seq OWNER TO postgres;

--
-- Name: maintenance_record_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.maintenance_record_id_seq OWNED BY public.maintenance_record.id;


--
-- Name: notification; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notification (
    id integer NOT NULL,
    user_id integer,
    title character varying(120),
    message text,
    is_read boolean,
    created_date timestamp without time zone,
    order_type character varying(64),
    order_id integer
);


ALTER TABLE public.notification OWNER TO postgres;

--
-- Name: notification_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notification_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.notification_id_seq OWNER TO postgres;

--
-- Name: notification_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notification_id_seq OWNED BY public.notification.id;


--
-- Name: part_replacement; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.part_replacement (
    id integer NOT NULL,
    repair_order_id integer,
    spare_part_id integer,
    quantity integer,
    replacement_date timestamp without time zone
);


ALTER TABLE public.part_replacement OWNER TO postgres;

--
-- Name: part_replacement_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.part_replacement_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.part_replacement_id_seq OWNER TO postgres;

--
-- Name: part_replacement_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.part_replacement_id_seq OWNED BY public.part_replacement.id;


--
-- Name: part_request_order; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.part_request_order (
    id integer NOT NULL,
    requester_id integer,
    department_head_id integer,
    admin_id integer,
    part_name character varying(120),
    part_number character varying(120),
    quantity integer,
    reason text,
    status character varying(64),
    department_head_approved boolean,
    admin_approved boolean,
    created_date timestamp without time zone,
    updated_date timestamp without time zone,
    completed_date timestamp without time zone
);


ALTER TABLE public.part_request_order OWNER TO postgres;

--
-- Name: part_request_order_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.part_request_order_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.part_request_order_id_seq OWNER TO postgres;

--
-- Name: part_request_order_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.part_request_order_id_seq OWNED BY public.part_request_order.id;


--
-- Name: permission; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permission (
    id integer NOT NULL,
    role_id integer,
    module character varying(64),
    action character varying(64),
    resource_type character varying(64),
    conditions text,
    is_granted boolean,
    priority integer,
    created_date timestamp without time zone
);


ALTER TABLE public.permission OWNER TO postgres;

--
-- Name: permission_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.permission_id_seq OWNER TO postgres;

--
-- Name: permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.permission_id_seq OWNED BY public.permission.id;


--
-- Name: repair_order; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.repair_order (
    id integer NOT NULL,
    equipment_id integer,
    requester_id integer,
    technician_id integer,
    department_head_id integer,
    admin_id integer,
    description text,
    repair_cost double precision,
    status character varying(64),
    created_date timestamp without time zone,
    updated_date timestamp without time zone,
    completed_date timestamp without time zone,
    department_head_approved boolean,
    admin_approved boolean
);


ALTER TABLE public.repair_order OWNER TO postgres;

--
-- Name: repair_order_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.repair_order_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repair_order_id_seq OWNER TO postgres;

--
-- Name: repair_order_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.repair_order_id_seq OWNED BY public.repair_order.id;


--
-- Name: role_definition; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.role_definition (
    id integer NOT NULL,
    name character varying(64),
    description text,
    is_custom boolean,
    is_active boolean,
    created_date timestamp without time zone,
    created_by_id integer
);


ALTER TABLE public.role_definition OWNER TO postgres;

--
-- Name: role_definition_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.role_definition_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.role_definition_id_seq OWNER TO postgres;

--
-- Name: role_definition_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.role_definition_id_seq OWNED BY public.role_definition.id;


--
-- Name: spare_part; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.spare_part (
    id integer NOT NULL,
    name character varying(120),
    part_number character varying(120),
    type_id integer,
    price double precision,
    stock_quantity integer,
    min_stock_level integer,
    department_id integer,
    department character varying(120),
    location character varying(120),
    purchase_date date,
    is_public boolean
);


ALTER TABLE public.spare_part OWNER TO postgres;

--
-- Name: spare_part_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.spare_part_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.spare_part_id_seq OWNER TO postgres;

--
-- Name: spare_part_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.spare_part_id_seq OWNED BY public.spare_part.id;


--
-- Name: spare_part_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.spare_part_type (
    id integer NOT NULL,
    name character varying(120) NOT NULL,
    description text,
    created_date timestamp without time zone
);


ALTER TABLE public.spare_part_type OWNER TO postgres;

--
-- Name: spare_part_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.spare_part_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.spare_part_type_id_seq OWNER TO postgres;

--
-- Name: spare_part_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.spare_part_type_id_seq OWNED BY public.spare_part_type.id;


--
-- Name: user_activity_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_activity_log (
    id integer NOT NULL,
    user_id integer,
    action character varying(120),
    description text,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.user_activity_log OWNER TO postgres;

--
-- Name: user_activity_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_activity_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_activity_log_id_seq OWNER TO postgres;

--
-- Name: user_activity_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_activity_log_id_seq OWNED BY public.user_activity_log.id;


--
-- Name: user_approval_role; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_approval_role (
    id integer NOT NULL,
    user_id integer NOT NULL,
    role_id integer NOT NULL,
    assigned_by_id integer,
    assigned_date timestamp without time zone,
    start_date timestamp without time zone,
    end_date timestamp without time zone,
    is_active boolean,
    notes text
);


ALTER TABLE public.user_approval_role OWNER TO postgres;

--
-- Name: user_approval_role_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_approval_role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_approval_role_id_seq OWNER TO postgres;

--
-- Name: user_approval_role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_approval_role_id_seq OWNED BY public.user_approval_role.id;


--
-- Name: user_custom_role; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_custom_role (
    user_id integer NOT NULL,
    role_id integer NOT NULL,
    assigned_by_id integer,
    assigned_date timestamp without time zone,
    expired_date timestamp without time zone,
    is_active boolean,
    notes character varying(500)
);


ALTER TABLE public.user_custom_role OWNER TO postgres;

--
-- Name: workflow_instance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workflow_instance (
    id integer NOT NULL,
    template_id integer,
    order_type character varying(64) NOT NULL,
    order_id integer NOT NULL,
    current_node_id integer,
    status character varying(32),
    started_at timestamp without time zone,
    finished_at timestamp without time zone
);


ALTER TABLE public.workflow_instance OWNER TO postgres;

--
-- Name: workflow_instance_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workflow_instance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workflow_instance_id_seq OWNER TO postgres;

--
-- Name: workflow_instance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workflow_instance_id_seq OWNED BY public.workflow_instance.id;


--
-- Name: workflow_node; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workflow_node (
    id integer NOT NULL,
    template_id integer NOT NULL,
    code character varying(64) NOT NULL,
    name character varying(128) NOT NULL,
    sequence integer NOT NULL,
    node_type character varying(32),
    approval_role_id integer,
    approver_user_ids text,
    condition_expr text,
    amount_threshold numeric(15,2),
    skip_if_below_threshold boolean,
    is_parallel boolean,
    required_approvals integer,
    parallel_mode character varying(32),
    timeout_hours integer,
    timeout_action character varying(32),
    escalate_to_role_id integer,
    auto_approve_rules json,
    auto_reject_rules json,
    notify_on_start boolean,
    notify_on_complete boolean,
    notify_methods json,
    is_active boolean,
    approver_user_id integer,
    actions_on_reject text,
    condition_expression text,
    parallel_count integer,
    escalate_to_user_id integer,
    role_required_name character varying(64)
);


ALTER TABLE public.workflow_node OWNER TO postgres;

--
-- Name: COLUMN workflow_node.condition_expression; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.workflow_node.condition_expression IS '条件表达式(Python)';


--
-- Name: COLUMN workflow_node.parallel_count; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.workflow_node.parallel_count IS '并行所需审批数';


--
-- Name: workflow_node_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workflow_node_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workflow_node_id_seq OWNER TO postgres;

--
-- Name: workflow_node_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workflow_node_id_seq OWNED BY public.workflow_node.id;


--
-- Name: workflow_template; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workflow_template (
    id integer NOT NULL,
    code character varying(64) NOT NULL,
    name character varying(128) NOT NULL,
    order_type character varying(64) NOT NULL,
    version integer,
    is_active boolean,
    is_default boolean,
    description text,
    config json,
    created_by_id integer,
    created_date timestamp without time zone,
    updated_date timestamp without time zone
);


ALTER TABLE public.workflow_template OWNER TO postgres;

--
-- Name: workflow_template_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workflow_template_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workflow_template_id_seq OWNER TO postgres;

--
-- Name: workflow_template_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workflow_template_id_seq OWNED BY public.workflow_template.id;


--
-- Name: account_request id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.account_request ALTER COLUMN id SET DEFAULT nextval('public.account_request_id_seq'::regclass);


--
-- Name: action_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.action_log ALTER COLUMN id SET DEFAULT nextval('public.action_log_id_seq'::regclass);


--
-- Name: announcement_attachment id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.announcement_attachment ALTER COLUMN id SET DEFAULT nextval('public.announcement_attachment_id_seq'::regclass);


--
-- Name: announcements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.announcements ALTER COLUMN id SET DEFAULT nextval('public.announcements_id_seq'::regclass);


--
-- Name: app_user id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_user ALTER COLUMN id SET DEFAULT nextval('public.app_user_id_seq'::regclass);


--
-- Name: approval_decision id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_decision ALTER COLUMN id SET DEFAULT nextval('public.approval_decision_id_seq'::regclass);


--
-- Name: approval_delegate id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_delegate ALTER COLUMN id SET DEFAULT nextval('public.approval_delegate_id_seq'::regclass);


--
-- Name: approval_instance id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_instance ALTER COLUMN id SET DEFAULT nextval('public.approval_instance_id_seq'::regclass);


--
-- Name: approval_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_log ALTER COLUMN id SET DEFAULT nextval('public.approval_log_id_seq'::regclass);


--
-- Name: approval_reminder id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_reminder ALTER COLUMN id SET DEFAULT nextval('public.approval_reminder_id_seq'::regclass);


--
-- Name: approval_role id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_role ALTER COLUMN id SET DEFAULT nextval('public.approval_role_id_seq'::regclass);


--
-- Name: approval_step id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_step ALTER COLUMN id SET DEFAULT nextval('public.approval_step_id_seq'::regclass);


--
-- Name: approval_workflow id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_workflow ALTER COLUMN id SET DEFAULT nextval('public.approval_workflow_id_seq'::regclass);


--
-- Name: asset_cost id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_cost ALTER COLUMN id SET DEFAULT nextval('public.asset_cost_id_seq'::regclass);


--
-- Name: asset_handover id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_handover ALTER COLUMN id SET DEFAULT nextval('public.asset_handover_id_seq'::regclass);


--
-- Name: asset_lifecycle id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_lifecycle ALTER COLUMN id SET DEFAULT nextval('public.asset_lifecycle_id_seq'::regclass);


--
-- Name: audit_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_log ALTER COLUMN id SET DEFAULT nextval('public.audit_log_id_seq'::regclass);


--
-- Name: chat_attachment id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_attachment ALTER COLUMN id SET DEFAULT nextval('public.chat_attachment_id_seq'::regclass);


--
-- Name: chat_conversation id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_conversation ALTER COLUMN id SET DEFAULT nextval('public.chat_conversation_id_seq'::regclass);


--
-- Name: chat_message id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_message ALTER COLUMN id SET DEFAULT nextval('public.chat_message_id_seq'::regclass);


--
-- Name: chat_participant id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_participant ALTER COLUMN id SET DEFAULT nextval('public.chat_participant_id_seq'::regclass);


--
-- Name: chat_permission id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_permission ALTER COLUMN id SET DEFAULT nextval('public.chat_permission_id_seq'::regclass);


--
-- Name: department id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.department ALTER COLUMN id SET DEFAULT nextval('public.department_id_seq'::regclass);


--
-- Name: equipment id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment ALTER COLUMN id SET DEFAULT nextval('public.equipment_id_seq'::regclass);


--
-- Name: equipment_application id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_application ALTER COLUMN id SET DEFAULT nextval('public.equipment_application_id_seq'::regclass);


--
-- Name: equipment_loan id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_loan ALTER COLUMN id SET DEFAULT nextval('public.equipment_loan_id_seq'::regclass);


--
-- Name: equipment_scrap id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_scrap ALTER COLUMN id SET DEFAULT nextval('public.equipment_scrap_id_seq'::regclass);


--
-- Name: equipment_transfer id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_transfer ALTER COLUMN id SET DEFAULT nextval('public.equipment_transfer_id_seq'::regclass);


--
-- Name: equipment_type id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_type ALTER COLUMN id SET DEFAULT nextval('public.equipment_type_id_seq'::regclass);


--
-- Name: inventory_warning id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory_warning ALTER COLUMN id SET DEFAULT nextval('public.inventory_warning_id_seq'::regclass);


--
-- Name: maintenance_plan id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maintenance_plan ALTER COLUMN id SET DEFAULT nextval('public.maintenance_plan_id_seq'::regclass);


--
-- Name: maintenance_record id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maintenance_record ALTER COLUMN id SET DEFAULT nextval('public.maintenance_record_id_seq'::regclass);


--
-- Name: notification id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification ALTER COLUMN id SET DEFAULT nextval('public.notification_id_seq'::regclass);


--
-- Name: part_replacement id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.part_replacement ALTER COLUMN id SET DEFAULT nextval('public.part_replacement_id_seq'::regclass);


--
-- Name: part_request_order id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.part_request_order ALTER COLUMN id SET DEFAULT nextval('public.part_request_order_id_seq'::regclass);


--
-- Name: permission id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permission ALTER COLUMN id SET DEFAULT nextval('public.permission_id_seq'::regclass);


--
-- Name: repair_order id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.repair_order ALTER COLUMN id SET DEFAULT nextval('public.repair_order_id_seq'::regclass);


--
-- Name: role_definition id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_definition ALTER COLUMN id SET DEFAULT nextval('public.role_definition_id_seq'::regclass);


--
-- Name: spare_part id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.spare_part ALTER COLUMN id SET DEFAULT nextval('public.spare_part_id_seq'::regclass);


--
-- Name: spare_part_type id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.spare_part_type ALTER COLUMN id SET DEFAULT nextval('public.spare_part_type_id_seq'::regclass);


--
-- Name: user_activity_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_activity_log ALTER COLUMN id SET DEFAULT nextval('public.user_activity_log_id_seq'::regclass);


--
-- Name: user_approval_role id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_approval_role ALTER COLUMN id SET DEFAULT nextval('public.user_approval_role_id_seq'::regclass);


--
-- Name: workflow_instance id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_instance ALTER COLUMN id SET DEFAULT nextval('public.workflow_instance_id_seq'::regclass);


--
-- Name: workflow_node id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_node ALTER COLUMN id SET DEFAULT nextval('public.workflow_node_id_seq'::regclass);


--
-- Name: workflow_template id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_template ALTER COLUMN id SET DEFAULT nextval('public.workflow_template_id_seq'::regclass);


--
-- Data for Name: account_request; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.account_request (id, username, full_name, employee_no, email, department, role_requested, reason, password_hash, status, created_date, processed_date, approver_id, approver_comments) FROM stdin;
\.


--
-- Data for Name: action_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.action_log (id, action_name, workflow_node_id, approval_workflow_id, payload, status, result, executed_at, retry_count) FROM stdin;
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
merge_e8f7_loan_return
patch_normalize_attachment_paths
\.


--
-- Data for Name: announcement_attachment; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.announcement_attachment (id, announcement_id, filename, stored_filename, file_path, file_size, file_type, thumbnail_path, upload_user_id, created_date, is_deleted, deleted_date) FROM stdin;
\.


--
-- Data for Name: announcements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.announcements (id, title, content, type, priority, is_pinned, is_published, publish_time, expire_time, created_at, updated_at, creator_id) FROM stdin;
\.


--
-- Data for Name: announcements_publish_time_backup; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.announcements_publish_time_backup (id, publish_time, created_at, backed_up_at) FROM stdin;
4	\N	2025-12-16 08:25:43.465321	2025-12-17 14:11:35.394431
5	\N	2025-12-16 08:48:13.945152	2025-12-17 14:11:35.394431
6	\N	2025-12-17 04:11:24.872196	2025-12-17 14:11:35.394431
\.


--
-- Data for Name: app_user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.app_user (id, username, email, password_hash, role, department_id, department, is_active, workflow_roles, can_manage_equipment, can_manage_spare_parts, can_manage_repairs, can_manage_part_requests, can_view_workflow, can_edit_workflow, can_manage_workflow_templates, can_view_reports, can_view_logs) FROM stdin;
8	陈松	ddd@ddd.com	pbkdf2:sha256:260000$mgKdvTS1o0lfOy6V$c6e13f9be058eba5952f81aa296e2e8d3d751587ff20311d963239444f05bde4	user	6	企管部	t	["department_head", "executive"]	f	f	f	f	f	f	f	f	f
7	admin	admin@example.com	pbkdf2:sha256:260000$vfRBHJzJ14x00Ek4$1120822a33e1cc8eee53ca118ef96f18be0308af4438673eaafc883a9fcb2b01	admin	\N	超级管理员	t	\N	f	f	f	f	f	f	f	f	f
\.


--
-- Data for Name: approval_decision; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.approval_decision (id, approval_workflow_id, approver_id, decision, comments, created_at) FROM stdin;
\.


--
-- Data for Name: approval_delegate; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.approval_delegate (id, user_id, delegate_to_id, order_types, role_ids, start_date, end_date, is_active, reason, created_date) FROM stdin;
\.


--
-- Data for Name: approval_instance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.approval_instance (id, instance_no, template_id, order_type, order_id, requester_id, requester_dept_id, status, current_node_id, started_date, completed_date, expected_complete_date, form_data, context_data, final_result, final_comment) FROM stdin;
1	CHAT-20251221060636	3	chat	3	7	\N	approved	\N	2025-12-21 06:06:36.818729	2025-12-21 06:06:36.842098	\N	{}	{"requester_id": 7, "order_type": "chat", "order_id": 3}	approved	
2	CHAT-20251221061511	3	chat	3	7	\N	approved	\N	2025-12-21 06:15:11.210346	2025-12-21 06:15:11.217803	\N	{}	{"requester_id": 7, "order_type": "chat", "order_id": 3}	approved	
3	CHAT-20251221062924	3	chat	3	7	\N	approved	\N	2025-12-21 06:29:24.855111	2025-12-21 06:29:24.861625	\N	{}	{"requester_id": 7, "order_type": "chat", "order_id": 3}	approved	
4	CHAT-20251221064222	3	chat	3	7	\N	approved	\N	2025-12-21 06:42:22.890205	2025-12-21 06:42:22.900333	\N	{}	{"requester_id": 7, "order_type": "chat", "order_id": 3}	approved	
5	CHAT-20251222002213	3	chat	3	7	\N	approved	\N	2025-12-22 00:22:13.81485	2025-12-22 00:22:13.826439	\N	{}	{"requester_id": 7, "order_type": "chat", "order_id": 3}	approved	
6	CHAT-20251222003933	3	chat	3	7	\N	approved	\N	2025-12-22 00:39:33.920726	2025-12-22 00:39:33.927452	\N	{}	{"requester_id": 7, "order_type": "chat", "order_id": 3}	approved	
\.


--
-- Data for Name: approval_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.approval_log (id, instance_id, step_id, action, operator_id, operator_role, old_value, new_value, comment, ip_address, user_agent, created_date) FROM stdin;
1	1	\N	start	7	\N	\N	\N	流程启动	\N	\N	2025-12-21 06:06:36.825902
2	1	\N	no_approver	\N	\N	\N	\N	节点 部门领导审批 未找到审批人,自动跳过	\N	\N	2025-12-21 06:06:36.836234
3	1	\N	no_approver	\N	\N	\N	\N	节点 管理员审批 未找到审批人,自动跳过	\N	\N	2025-12-21 06:06:36.83991
4	1	\N	complete	\N	\N	\N	\N	流程完成,结果: approved	\N	\N	2025-12-21 06:06:36.84384
5	2	\N	start	7	\N	\N	\N	流程启动	\N	\N	2025-12-21 06:15:11.211487
6	2	\N	no_approver	\N	\N	\N	\N	节点 部门领导审批 未找到审批人,自动跳过	\N	\N	2025-12-21 06:15:11.214783
7	2	\N	no_approver	\N	\N	\N	\N	节点 管理员审批 未找到审批人,自动跳过	\N	\N	2025-12-21 06:15:11.216658
8	2	\N	complete	\N	\N	\N	\N	流程完成,结果: approved	\N	\N	2025-12-21 06:15:11.218603
9	3	\N	start	7	\N	\N	\N	流程启动	\N	\N	2025-12-21 06:29:24.856184
10	3	\N	no_approver	\N	\N	\N	\N	节点 部门领导审批 未找到审批人,自动跳过	\N	\N	2025-12-21 06:29:24.85886
11	3	\N	no_approver	\N	\N	\N	\N	节点 管理员审批 未找到审批人,自动跳过	\N	\N	2025-12-21 06:29:24.860595
12	3	\N	complete	\N	\N	\N	\N	流程完成,结果: approved	\N	\N	2025-12-21 06:29:24.862419
13	4	\N	start	7	\N	\N	\N	流程启动	\N	\N	2025-12-21 06:42:22.892016
14	4	\N	no_approver	\N	\N	\N	\N	节点 部门领导审批 未找到审批人,自动跳过	\N	\N	2025-12-21 06:42:22.897642
15	4	\N	no_approver	\N	\N	\N	\N	节点 管理员审批 未找到审批人,自动跳过	\N	\N	2025-12-21 06:42:22.899602
16	4	\N	complete	\N	\N	\N	\N	流程完成,结果: approved	\N	\N	2025-12-21 06:42:22.901088
17	5	\N	start	7	\N	\N	\N	流程启动	\N	\N	2025-12-22 00:22:13.817061
18	5	\N	no_approver	\N	\N	\N	\N	节点 部门领导审批 未找到审批人,自动跳过	\N	\N	2025-12-22 00:22:13.822774
19	5	\N	no_approver	\N	\N	\N	\N	节点 管理员审批 未找到审批人,自动跳过	\N	\N	2025-12-22 00:22:13.825528
20	5	\N	complete	\N	\N	\N	\N	流程完成,结果: approved	\N	\N	2025-12-22 00:22:13.827215
21	6	\N	start	7	\N	\N	\N	流程启动	\N	\N	2025-12-22 00:39:33.921825
22	6	\N	no_approver	\N	\N	\N	\N	节点 部门领导审批 未找到审批人,自动跳过	\N	\N	2025-12-22 00:39:33.925117
23	6	\N	no_approver	\N	\N	\N	\N	节点 管理员审批 未找到审批人,自动跳过	\N	\N	2025-12-22 00:39:33.926706
24	6	\N	complete	\N	\N	\N	\N	流程完成,结果: approved	\N	\N	2025-12-22 00:39:33.928003
\.


--
-- Data for Name: approval_reminder; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.approval_reminder (id, step_id, reminder_type, sent_to_id, sent_date, send_method, is_sent, sent_result) FROM stdin;
\.


--
-- Data for Name: approval_role; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.approval_role (id, code, name, description, category, level, icon, color, can_approve_repair, can_approve_part_request, can_approve_equipment_transfer, can_approve_equipment_scrap, can_approve_equipment_loan, can_approve_equipment_application, max_approval_amount, is_active, is_system_role, created_date, updated_date, created_by_id) FROM stdin;
1	o_d	测试	如果以后	custom	10	fa-user	#6c757d	t	t	t	t	t	t	\N	f	f	2025-12-16 10:38:07.164899	2025-12-20 08:36:37.582067	\N
2	admin	系统管理员	拥有所有审批权限	system	100	fa-user-tie	#4e73df	t	t	t	t	t	t	\N	t	t	2025-12-20 09:01:01.293033	2025-12-20 09:01:01.293033	\N
3	department_head	部门负责人	部门主管,可审批部门内工单	system	50	fa-user-tie	#1cc88a	t	t	t	f	t	t	10000	t	t	2025-12-20 09:01:01.293033	2025-12-20 09:01:01.293033	\N
4	technician	技术员	技术人员,可审批维修相关工单	system	30	fa-wrench	#36b9cc	t	t	f	f	f	f	5000	t	t	2025-12-20 09:01:01.293033	2025-12-20 09:01:01.293033	\N
5	warehouse	仓库管理员	仓库管理人员,可审批配件相关工单	system	30	fa-box	#f6c23e	f	t	t	f	t	f	3000	t	t	2025-12-20 09:01:01.293033	2025-12-20 09:01:01.293033	\N
6	finance	财务审批	财务人员,可审批高金额工单	system	70	fa-dollar-sign	#e74a3b	t	t	t	t	f	t	\N	t	t	2025-12-20 09:01:01.293033	2025-12-20 09:01:01.293033	\N
\.


--
-- Data for Name: approval_step; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.approval_step (id, instance_id, node_id, sequence, step_no, approver_id, approver_role_id, assigned_date, parallel_group_id, parallel_approvers, approved_count, status, result, comment, approved_date, transferred_from_id, transferred_to_id, transfer_reason, deadline, is_timeout, timeout_handled_date, admin_action, admin_operator_id, admin_comment) FROM stdin;
\.


--
-- Data for Name: approval_workflow; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.approval_workflow (id, order_type, order_id, approver_id, approval_level, node_id, status, comments, created_date, approved_date, auto_assigned, action_type, repair_cost_input, transferred_from_id, admin_action, admin_operator_id, required_approvals, actions_on_reject) FROM stdin;
\.


--
-- Data for Name: asset_cost; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.asset_cost (id, equipment_id, purchase_price, purchase_date, maintenance_cost, depreciation_rate, residual_value, depreciation_method, expected_lifespan, supplier, warranty_period, created_date, updated_date) FROM stdin;
\.


--
-- Data for Name: asset_handover; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.asset_handover (id, from_user_id, to_user_id, equipment_ids, status, reason, reason_detail, created_date, completed_date, completed_by_id) FROM stdin;
\.


--
-- Data for Name: asset_lifecycle; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.asset_lifecycle (id, equipment_id, event_type, event_date, old_status, new_status, description, responsible_user_id, cost_involved, documents) FROM stdin;
\.


--
-- Data for Name: audit_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_log (id, user_id, action_type, resource_type, resource_id, old_value, new_value, ip_address, reason, created_date) FROM stdin;
\.


--
-- Data for Name: chat_attachment; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chat_attachment (id, message_id, filename, stored_filename, file_path, file_size, file_type, thumbnail_path, created_date, upload_user_id) FROM stdin;
4	19	playwright_test_file.txt	1365df9d3c294382ba665637fb98af42.txt	uploads/chat/1365df9d3c294382ba665637fb98af42.txt	22	text/plain	\N	2025-12-21 14:06:36.889594	7
5	22	playwright_test_file.txt	5f42cdf54321406bb45be501dcedaea5.txt	uploads/chat/5f42cdf54321406bb45be501dcedaea5.txt	22	text/plain	\N	2025-12-21 14:15:11.254425	7
6	\N	test_img.png	8eaf8dfa8ff0472e93cbb25bf9c4c231.png	uploads/chat/8eaf8dfa8ff0472e93cbb25bf9c4c231.png	204	image/png	uploads/chat/thumb_8eaf8dfa8ff0472e93cbb25bf9c4c231.png	2025-12-21 14:15:11.372263	7
7	25	playwright_test_file.txt	1e03325a1a2948cbb282efcbed69228a.txt	uploads/chat/1e03325a1a2948cbb282efcbed69228a.txt	22	text/plain	\N	2025-12-21 14:29:24.913123	7
8	\N	test_img.png	f0df830e43964fc2bf6c239894bda004.png	uploads/chat/f0df830e43964fc2bf6c239894bda004.png	204	image/png	uploads/chat/thumb_f0df830e43964fc2bf6c239894bda004.png	2025-12-21 14:29:25.011816	7
9	28	playwright_test_file.txt	743e8944041f455ca9a22e0b703d50f4.txt	/app/uploads/chat/743e8944041f455ca9a22e0b703d50f4.txt	22	text/plain	\N	2025-12-21 14:42:22.943755	7
11	31	playwright_test_file.txt	c704390cb9044dbb975083f8b8071069.txt	/app/uploads/chat/c704390cb9044dbb975083f8b8071069.txt	22	text/plain	\N	2025-12-22 08:22:13.875243	7
13	34	playwright_test_file.txt	6af977e2de934a38a51809c95f26c193.txt	/app/uploads/chat/6af977e2de934a38a51809c95f26c193.txt	22	text/plain	\N	2025-12-22 08:39:33.975097	7
10	\N	test_img.png	94f664bf0ae545f09924cc825c89aa6d.png	/app/uploads/chat/94f664bf0ae545f09924cc825c89aa6d.png	204	image/png	/app/uploads/chat/thumb_94f664bf0ae545f09924cc825c89aa6d.png	2025-12-21 14:42:23.052581	7
12	\N	test_img.png	bf8b3c5c69a543288c150b7ac3415e43.png	/app/uploads/chat/bf8b3c5c69a543288c150b7ac3415e43.png	204	image/png	/app/uploads/chat/thumb_bf8b3c5c69a543288c150b7ac3415e43.png	2025-12-22 08:22:14.018423	7
14	\N	test_img.png	154b48c87c4a47cdb598fbd5c9c700bb.png	/app/uploads/chat/154b48c87c4a47cdb598fbd5c9c700bb.png	204	image/png	/app/uploads/chat/thumb_154b48c87c4a47cdb598fbd5c9c700bb.png	2025-12-22 08:39:34.099009	7
\.


--
-- Data for Name: chat_conversation; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chat_conversation (id, conversation_type, name, avatar_url, description, creator_id, is_active, created_date, updated_date, last_message_id, last_message_time) FROM stdin;
2	direct		\N	\N	7	t	2025-12-16 10:57:10.54395	2025-12-20 16:24:21.595645	5	2025-12-20 16:24:21.594089
3	direct	\N	\N	\N	7	t	2025-12-20 16:15:08.86681	2025-12-22 08:50:04.014162	35	2025-12-22 08:50:04.012646
\.


--
-- Data for Name: chat_message; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chat_message (id, conversation_id, sender_id, message_type, content, is_recalled, recalled_date, is_deleted, created_date, reply_to_message_id) FROM stdin;
1	3	7	text	你在做什么	f	\N	f	2025-12-20 16:15:20.403111	\N
2	3	7	text	实时 tail web 日志	f	\N	f	2025-12-20 16:23:54.097837	\N
3	3	7	text	55	f	\N	f	2025-12-20 16:24:03.934098	\N
4	3	7	text	你呢	f	\N	f	2025-12-20 16:24:16.217669	\N
5	2	7	text	555	f	\N	f	2025-12-20 16:24:21.594089	\N
6	3	7	text	55	f	\N	f	2025-12-20 17:18:36.841035	\N
7	3	8	text	好的	f	\N	f	2025-12-20 18:36:23.604071	\N
8	3	7	text	？	f	\N	f	2025-12-20 18:49:08.713766	\N
9	3	7	text	Playwright automated message	f	\N	f	2025-12-21 13:36:35.064023	\N
10	3	7	text	Playwright automated message	f	\N	f	2025-12-21 13:41:13.725405	\N
11	3	7	text	Playwright automated message	f	\N	f	2025-12-21 13:42:08.750138	\N
12	3	7	text	Playwright automated message	f	\N	f	2025-12-21 13:43:38.212145	\N
13	3	7	text	Playwright automated message	f	\N	f	2025-12-21 13:45:59.865904	\N
14	3	7	text	Playwright automated message	f	\N	f	2025-12-21 13:46:19.064708	\N
15	3	7	text	Playwright automated message	f	\N	f	2025-12-21 13:46:56.754533	\N
16	3	7	text	Playwright automated message	f	\N	f	2025-12-21 13:59:23.491395	\N
17	3	7	text	Playwright automated message	f	\N	f	2025-12-21 14:06:36.786946	\N
18	3	7	system	已发起审批流程: 默认流程模板 (实例ID: 1)	f	\N	f	2025-12-21 14:06:36.849501	\N
19	3	7	text	Playwright uploaded file	f	\N	f	2025-12-21 14:06:36.904417	\N
20	3	7	text	Playwright automated message	f	\N	f	2025-12-21 14:15:11.187177	\N
21	3	7	system	已发起审批流程: 默认流程模板 (实例ID: 2)	f	\N	f	2025-12-21 14:15:11.221966	\N
22	3	7	text	Playwright uploaded file	f	\N	f	2025-12-21 14:15:11.268192	\N
23	3	7	text	Playwright automated message	f	\N	f	2025-12-21 14:29:24.813782	\N
24	3	7	system	已发起审批流程: 默认流程模板 (实例ID: 3)	f	\N	f	2025-12-21 14:29:24.867144	\N
25	3	7	text	Playwright uploaded file	f	\N	f	2025-12-21 14:29:24.928274	\N
26	3	7	text	Playwright automated message	f	\N	f	2025-12-21 14:42:22.862362	\N
27	3	7	system	已发起审批流程: 默认流程模板 (实例ID: 4)	f	\N	f	2025-12-21 14:42:22.905632	\N
28	3	7	text	Playwright uploaded file	f	\N	f	2025-12-21 14:42:22.95926	\N
29	3	7	text	Playwright automated message	f	\N	f	2025-12-22 08:22:13.784191	\N
30	3	7	system	已发起审批流程: 默认流程模板 (实例ID: 5)	f	\N	f	2025-12-22 08:22:13.832185	\N
31	3	7	text	Playwright uploaded file	f	\N	f	2025-12-22 08:22:13.88956	\N
32	3	7	text	Playwright automated message	f	\N	f	2025-12-22 08:39:33.897152	\N
33	3	7	system	已发起审批流程: 默认流程模板 (实例ID: 6)	f	\N	f	2025-12-22 08:39:33.93118	\N
34	3	7	text	Playwright uploaded file	f	\N	f	2025-12-22 08:39:33.992157	\N
35	3	7	text	UI	f	\N	f	2025-12-22 08:50:04.012646	\N
\.


--
-- Data for Name: chat_participant; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chat_participant (id, conversation_id, user_id, joined_date, last_read_message_id, unread_count, is_pinned, is_muted, is_left, left_date, role) FROM stdin;
3	2	7	2025-12-16 10:57:10.544831	\N	0	f	f	f	\N	member
4	3	7	2025-12-20 16:15:08.869402	\N	1	f	f	f	\N	member
5	3	8	2025-12-20 16:15:08.869413	\N	19	f	f	f	\N	member
\.


--
-- Data for Name: chat_permission; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chat_permission (id, user_id, can_send_message, can_send_file, can_create_group, muted_until, notes, operated_by_id, operated_date) FROM stdin;
\.


--
-- Data for Name: department; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.department (id, name, code, cost_center, location, description) FROM stdin;
1	信息部	IT	CC001	A座5楼	信息技术部门
2	财务部	FIN	CC002	A座3楼	财务管理部门
3	人力行政部	HR	CC003	A座2楼	人力资源部门
4	国内销售中心	SALES	CC004	B座1楼	销售部门
5	生产办	PROD	CC005	C厂房	生产制造部门
6	企管部	ADMIN	CC006	A座4楼	企业管理部门
\.


--
-- Data for Name: equipment; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.equipment (id, name, type_id, type, brand, model, serial_number, equipment_number, purchase_date, price, department_id, department, location, status, is_public_pool, require_return_inspection, allow_loan) FROM stdin;
1	办公电脑001	\N	电脑	联想	ThinkCentre M720	PC2023001	\N	\N	0	2	财务部	\N	active	f	f	t
2	激光打印机001	2	打印机	惠普	LaserJet Pro MFP M428fdw	PR2023001	\N	2025-12-17	6666	1	信息部	信息部	active	f	f	t
\.


--
-- Data for Name: equipment_application; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.equipment_application (id, equipment_id, applicant_id, applicant_dept, reason, status, created_date, approved_date) FROM stdin;
\.


--
-- Data for Name: equipment_loan; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.equipment_loan (id, equipment_id, requester_id, requester_dept, start_date, end_date, status, approved_by, approved_date, borrowed_date, return_request_date, return_notes, return_condition, inspected_by, inspection_date, inspection_notes, inspection_result, damage_compensation, damage_description, returned_date, notes, pickup_notified, created_date, updated_date) FROM stdin;
\.


--
-- Data for Name: equipment_scrap; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.equipment_scrap (id, equipment_id, requester_id, description, status, created_date, updated_date, disposal_method, disposal_date, disposal_handler, disposal_notes, disposal_value, disposal_company, financial_cleared, financial_cleared_date, financial_cleared_by, financial_notes) FROM stdin;
\.


--
-- Data for Name: equipment_transfer; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.equipment_transfer (id, equipment_id, from_department, to_department, requester_id, description, status, created_date, updated_date) FROM stdin;
\.


--
-- Data for Name: equipment_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.equipment_type (id, name, description, created_date) FROM stdin;
1	电脑	包括台式机、笔记本等计算设备	2025-12-16 10:35:11.41839
2	打印机	各类打印设备	2025-12-16 10:35:11.418407
3	投影仪	投影显示设备	2025-12-16 10:35:11.418412
4	服务器	服务器设备	2025-12-16 10:35:11.418419
5	网络设备	路由器、交换机等网络设备	2025-12-16 10:35:11.418424
6	办公设备	其他办公设备	2025-12-16 10:35:11.418431
7	移动设备	手机、平板等移动设备	2025-12-16 10:35:11.418436
\.


--
-- Data for Name: inventory_warning; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.inventory_warning (id, spare_part_id, min_threshold, critical_threshold, reorder_quantity, lead_time_days, enabled, last_warned_date, created_date) FROM stdin;
\.


--
-- Data for Name: maintenance_plan; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.maintenance_plan (id, equipment_id, plan_name, maintenance_type, interval_days, next_maintenance_date, last_maintenance_date, responsible_person, description, is_active, created_by, created_date, updated_date) FROM stdin;
\.


--
-- Data for Name: maintenance_record; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.maintenance_record (id, plan_id, equipment_id, maintenance_date, maintenance_type, performed_by, description, notes, cost, next_maintenance_date, status, created_date) FROM stdin;
\.


--
-- Data for Name: notification; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notification (id, user_id, title, message, is_read, created_date, order_type, order_id) FROM stdin;
\.


--
-- Data for Name: part_replacement; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.part_replacement (id, repair_order_id, spare_part_id, quantity, replacement_date) FROM stdin;
\.


--
-- Data for Name: part_request_order; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.part_request_order (id, requester_id, department_head_id, admin_id, part_name, part_number, quantity, reason, status, department_head_approved, admin_approved, created_date, updated_date, completed_date) FROM stdin;
\.


--
-- Data for Name: permission; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.permission (id, role_id, module, action, resource_type, conditions, is_granted, priority, created_date) FROM stdin;
1	1	report	view	\N	\N	t	0	2025-12-20 09:08:28.492307
2	1	department	view	\N	\N	t	0	2025-12-20 09:08:28.492324
3	1	workflow	view	\N	\N	t	0	2025-12-20 09:08:28.492331
4	1	logs	view	\N	\N	t	0	2025-12-20 09:08:28.492336
5	1	announcement	view	\N	\N	t	0	2025-12-20 09:08:28.492341
6	1	announcement	create	\N	\N	t	0	2025-12-20 09:08:28.492345
7	1	announcement	edit	\N	\N	t	0	2025-12-20 09:08:28.492349
8	1	announcement	delete	\N	\N	t	0	2025-12-20 09:08:28.492354
9	1	announcement	publish	\N	\N	t	0	2025-12-20 09:08:28.492358
10	1	wework	view	\N	\N	t	0	2025-12-20 09:08:28.492362
\.


--
-- Data for Name: repair_order; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.repair_order (id, equipment_id, requester_id, technician_id, department_head_id, admin_id, description, repair_cost, status, created_date, updated_date, completed_date, department_head_approved, admin_approved) FROM stdin;
\.


--
-- Data for Name: role_definition; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.role_definition (id, name, description, is_custom, is_active, created_date, created_by_id) FROM stdin;
1	部门主管	用于部门管理	t	t	2025-12-20 09:07:54.055363	7
\.


--
-- Data for Name: spare_part; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.spare_part (id, name, part_number, type_id, price, stock_quantity, min_stock_level, department_id, department, location, purchase_date, is_public) FROM stdin;
1	内存条 8GB DDR4	MEM001	\N	280	10	10	\N	\N	\N	\N	f
2	固态硬盘 256GB SATA	SSD001	\N	180	5	10	\N	\N	\N	\N	f
3	电源适配器 65W	PWR001	\N	95	8	10	\N	\N	\N	\N	f
\.


--
-- Data for Name: spare_part_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.spare_part_type (id, name, description, created_date) FROM stdin;
1	lkiu		2025-12-16 10:36:36.670994
\.


--
-- Data for Name: user_activity_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_activity_log (id, user_id, action, description, "timestamp") FROM stdin;
1	7	用户登录	用户 admin 登录系统	2025-12-16 10:35:21.066833
2	7	访问页面	资产/配件管理中心 (IP: 172.19.0.1)	2025-12-16 10:35:42.304778
3	7	访问页面	设备列表 (IP: 172.19.0.1)	2025-12-16 10:35:44.461223
4	7	打印标签	equipment#3 (IP: 172.19.0.1)	2025-12-16 10:35:50.157645
5	7	删除设备	删除设备 办公电脑002 SN:PC2023002 (IP: 172.19.0.1)	2025-12-16 10:36:10.406937
6	7	访问页面	设备列表 (IP: 172.19.0.1)	2025-12-16 10:36:10.42787
7	7	访问页面	配件列表 (IP: 172.19.0.1)	2025-12-16 10:36:22.68963
8	7	访问页面	配件类型管理 (IP: 172.19.0.1)	2025-12-16 10:36:32.572364
9	7	添加配件类型	添加类型 lkiu (IP: 172.19.0.1)	2025-12-16 10:36:36.674241
10	7	访问页面	配件类型管理 (IP: 172.19.0.1)	2025-12-16 10:36:37.853364
11	7	访问页面	配件列表 (IP: 172.19.0.1)	2025-12-16 10:36:41.216083
12	7	访问页面	配件列表 (IP: 172.19.0.1)	2025-12-16 10:36:49.486997
13	7	访问页面	公开仓库 (IP: 172.19.0.1)	2025-12-16 10:40:00.743035
14	7	访问页面	公开仓库 (IP: 172.19.0.1)	2025-12-16 10:40:03.639039
15	7	访问页面	公开仓库 (IP: 172.19.0.1)	2025-12-16 10:40:04.875501
16	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 10:40:18.053111
17	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 10:40:29.863606
18	7	创建用户	管理员 admin 创建了用户 陈松 (IP: 172.19.0.1)	2025-12-16 10:41:13.301106
19	7	访问页面	部门管理 (IP: 172.19.0.1)	2025-12-16 10:52:48.685471
20	7	用户登录	用户 admin 登录系统	2025-12-16 10:53:45.792229
21	7	用户登录	用户 admin 登录系统	2025-12-16 10:54:26.536196
22	7	用户登录	用户 admin 登录系统	2025-12-16 10:57:10.523247
23	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 11:38:54.511955
24	7	创建公告	创建公告: 已他 (ID: 1) (IP: 172.19.0.1)	2025-12-16 11:39:08.314851
25	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 11:39:08.324627
26	7	查看公告详情	查看公告: 已他 (ID: 1) (IP: 172.19.0.1)	2025-12-16 11:39:13.536751
27	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-16 11:39:18.989432
28	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 11:39:20.249855
29	7	编辑公告	编辑公告: 已他 (ID: 1) (IP: 172.19.0.1)	2025-12-16 11:40:10.950632
30	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 11:40:10.96074
31	7	查看公告详情	查看公告: 已他 (ID: 1) (IP: 172.19.0.1)	2025-12-16 11:40:16.788747
32	7	查看公告详情	查看公告: 已他 (ID: 1) (IP: 172.19.0.1)	2025-12-16 11:43:03.508733
33	7	编辑公告	编辑公告: 已他 (ID: 1) (IP: 172.19.0.1)	2025-12-16 11:43:19.650455
34	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 11:43:19.660297
35	7	查看公告详情	查看公告: 已他 (ID: 1) (IP: 172.19.0.1)	2025-12-16 11:43:21.357361
36	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-16 11:43:24.6929
37	7	查看公告详情	查看公告: 已他 (ID: 1) (IP: 172.19.0.1)	2025-12-16 11:43:25.953969
38	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 11:43:30.088665
39	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-16 11:44:16.895273
40	7	查看公告详情	查看公告: 已他 (ID: 1) (IP: 172.19.0.1)	2025-12-16 11:44:17.775693
41	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-16 11:44:20.13754
42	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-16 11:44:23.689632
43	7	查看公告详情	查看公告: 已他 (ID: 1) (IP: 172.19.0.1)	2025-12-16 11:44:24.512688
44	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-16 11:44:44.517781
45	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 11:44:45.972859
46	7	查看公告详情	查看公告: 已他 (ID: 1) (IP: 172.19.0.1)	2025-12-16 11:44:47.58018
47	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-16 13:32:23.197
48	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 13:32:24.343968
49	7	查看公告详情	查看公告: 已他 (ID: 1) (IP: 172.19.0.1)	2025-12-16 13:32:26.405416
50	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-16 13:32:32.426333
51	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 13:32:33.157488
52	7	用户登录	用户 admin 登录系统	2025-12-16 15:32:25.564106
53	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-16 15:32:26.752728
54	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 15:32:27.588883
55	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-16 15:35:53.385613
56	7	查看公告详情	查看公告: 已他 (ID: 1) (IP: 172.19.0.1)	2025-12-16 15:35:54.232175
57	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 15:35:59.215906
58	7	创建公告	创建公告: 都打开 (ID: 2) (IP: 172.19.0.1)	2025-12-16 15:37:34.838861
59	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 15:37:34.852548
60	7	查看公告详情	查看公告: 都打开 (ID: 2) (IP: 172.19.0.1)	2025-12-16 15:37:38.936756
61	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 15:39:06.850921
62	7	删除公告	删除公告: 已他 (ID: 1) (IP: 172.19.0.1)	2025-12-16 15:39:11.551035
63	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 15:39:12.611858
64	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-16 15:39:29.72633
65	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 15:39:30.733959
66	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-16 15:41:34.299808
67	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 15:41:34.980833
68	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 15:42:05.216847
69	7	查看公告详情	查看公告: 都打开 (ID: 2) (IP: 172.19.0.1)	2025-12-16 15:42:08.585655
70	7	编辑公告	编辑公告: 都打开 (ID: 2) (IP: 172.19.0.1)	2025-12-16 15:42:18.790716
71	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 15:42:18.80131
72	7	查看公告详情	查看公告: 都打开 (ID: 2) (IP: 172.19.0.1)	2025-12-16 15:42:23.20409
73	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-16 15:42:26.80962
74	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 15:42:28.184591
75	7	查看公告详情	查看公告: 都打开 (ID: 2) (IP: 172.19.0.1)	2025-12-16 15:42:30.13744
76	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-16 15:42:31.399385
77	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 15:42:32.88967
78	7	删除公告	删除公告: 都打开 (ID: 2) (IP: 172.19.0.1)	2025-12-16 15:42:35.753472
79	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 15:42:37.027554
80	7	创建公告	创建公告: 灌灌灌灌灌 (ID: 3) (IP: 172.19.0.1)	2025-12-16 15:42:58.39227
81	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 15:42:58.405887
84	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-16 15:44:31.311051
87	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 15:44:36.468704
90	7	查看公告详情	查看公告: 灌灌灌灌灌 (ID: 3) (IP: 172.19.0.1)	2025-12-16 15:45:53.501904
92	7	访问页面	部门管理 (IP: 172.19.0.1)	2025-12-16 15:48:34.915696
93	7	访问页面	资产/配件管理中心 (IP: 172.19.0.1)	2025-12-16 15:48:48.978824
95	7	更新设备	更新设备 激光打印机001#2 (IP: 172.19.0.1)	2025-12-16 15:49:13.632896
82	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 15:43:03.756145
85	7	查看公告详情	查看公告: 灌灌灌灌灌 (ID: 3) (IP: 172.19.0.1)	2025-12-16 15:44:32.479019
88	7	查看公告详情	查看公告: 灌灌灌灌灌 (ID: 3) (IP: 172.19.0.1)	2025-12-16 15:44:43.113759
94	7	访问页面	设备列表 (IP: 172.19.0.1)	2025-12-16 15:48:50.286782
96	7	访问页面	设备列表 (IP: 172.19.0.1)	2025-12-16 15:49:13.648647
97	7	打印标签	equipment#2 (IP: 172.19.0.1)	2025-12-16 15:49:17.987016
98	7	查看公告详情	查看公告: 灌灌灌灌灌 (ID: 3) (IP: 172.19.0.1)	2025-12-16 15:49:39.301068
101	7	查看公告详情	查看公告: 灌灌灌灌灌 (ID: 3) (IP: 172.19.0.1)	2025-12-16 16:17:47.299104
103	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 16:17:54.678902
106	7	查看公告详情	查看公告: 灌灌灌灌灌 (ID: 3) (IP: 172.19.0.1)	2025-12-16 16:20:05.139229
109	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 16:20:22.736427
83	7	查看公告详情	查看公告: 灌灌灌灌灌 (ID: 3) (IP: 172.19.0.1)	2025-12-16 15:43:09.495516
86	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-16 15:44:35.617391
89	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 15:45:48.681997
91	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 15:47:06.547765
99	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 15:49:45.582605
100	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-16 16:17:46.424447
102	7	编辑公告	编辑公告: 灌灌灌灌灌 (ID: 3) (IP: 172.19.0.1)	2025-12-16 16:17:54.667762
104	7	查看公告详情	查看公告: 灌灌灌灌灌 (ID: 3) (IP: 172.19.0.1)	2025-12-16 16:17:58.393059
105	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-16 16:20:04.357879
107	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 16:20:08.917123
108	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 16:20:18.402408
110	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 16:21:34.623886
111	7	查看公告详情	查看公告: 灌灌灌灌灌 (ID: 3) (IP: 172.19.0.1)	2025-12-16 16:21:36.285815
112	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-16 16:24:42.198848
113	7	查看公告详情	查看公告: 灌灌灌灌灌 (ID: 3) (IP: 172.19.0.1)	2025-12-16 16:24:43.262359
114	7	查看公告详情	查看公告: 灌灌灌灌灌 (ID: 3) (IP: 172.19.0.1)	2025-12-16 16:25:21.961746
115	7	编辑公告	编辑公告: 灌灌灌灌灌 (ID: 3) (IP: 172.19.0.1)	2025-12-16 16:25:27.004708
116	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 16:25:27.014847
117	7	查看公告详情	查看公告: 灌灌灌灌灌 (ID: 3) (IP: 172.19.0.1)	2025-12-16 16:25:28.602478
118	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-16 16:25:30.80396
119	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 16:25:32.12078
120	7	删除公告	删除公告: 灌灌灌灌灌 (ID: 3) (IP: 172.19.0.1)	2025-12-16 16:25:34.539141
121	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 16:25:35.840204
122	7	创建公告	创建公告: 额三反五反 (ID: 4) (IP: 172.19.0.1)	2025-12-16 16:25:43.469641
123	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 16:25:43.48008
124	7	查看公告详情	查看公告: 额三反五反 (ID: 4) (IP: 172.19.0.1)	2025-12-16 16:25:45.441196
125	7	用户登录	用户 admin 登录系统	2025-12-16 16:47:59.709346
126	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-16 16:48:00.83047
127	7	查看公告详情	查看公告: 额三反五反 (ID: 4) (IP: 172.19.0.1)	2025-12-16 16:48:01.648707
128	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-16 16:48:04.198273
129	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 16:48:04.951152
130	7	创建公告	创建公告: 用 (ID: 5) (IP: 172.19.0.1)	2025-12-16 16:48:13.948133
131	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-16 16:48:13.958113
132	7	查看公告详情	查看公告: 用 (ID: 5) (IP: 172.19.0.1)	2025-12-16 16:48:16.336883
133	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-16 16:48:18.023955
134	7	查看公告详情	查看公告: 用 (ID: 5) (IP: 172.19.0.1)	2025-12-16 16:48:19.925568
135	7	查看公告详情	查看公告: 额三反五反 (ID: 4) (IP: 172.19.0.1)	2025-12-17 11:45:03.394913
136	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-17 11:45:05.793896
137	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-17 11:45:14.260576
138	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-17 11:45:40.487771
139	7	查看公告详情	查看公告: 用 (ID: 5) (IP: 172.19.0.1)	2025-12-17 12:10:42.462956
140	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-17 12:11:15.37706
141	7	查看公告详情	查看公告: 额三反五反 (ID: 4) (IP: 172.19.0.1)	2025-12-17 12:11:16.489303
142	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-17 12:11:17.962808
143	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-17 12:11:18.780085
144	7	创建公告	创建公告: 骨灰盒 (ID: 6) (IP: 172.19.0.1)	2025-12-17 12:11:24.875991
145	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-17 12:11:24.895967
146	7	查看公告详情	查看公告: 骨灰盒 (ID: 6) (IP: 172.19.0.1)	2025-12-17 12:11:27.250718
147	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-17 12:11:29.501064
148	7	查看公告详情	查看公告: 额三反五反 (ID: 4) (IP: 172.19.0.1)	2025-12-17 12:13:53.616997
149	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-17 12:13:55.3068
150	7	查看公告详情	查看公告: 骨灰盒 (ID: 6) (IP: 172.19.0.1)	2025-12-17 12:13:58.43993
151	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-17 12:14:00.72808
152	7	访问页面	配件列表 (IP: 172.19.0.1)	2025-12-17 13:24:00.147166
153	7	访问页面	设备列表 (IP: 172.19.0.1)	2025-12-17 13:24:03.54109
154	7	访问页面	设备类型管理 (IP: 172.19.0.1)	2025-12-17 13:24:17.290772
155	7	导出设备类型	导出设备类型数据 共 7 条 (IP: 172.19.0.1)	2025-12-17 13:24:21.027992
156	7	访问页面	部门管理 (IP: 172.19.0.1)	2025-12-17 13:24:25.862185
157	7	查看公告详情	查看公告: 额三反五反 (ID: 4) (IP: 172.19.0.1)	2025-12-17 13:24:49.96115
158	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-17 13:24:53.107574
159	7	查看公告详情	查看公告: 骨灰盒 (ID: 6) (IP: 172.19.0.1)	2025-12-17 13:24:59.52738
160	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-17 14:01:30.856765
161	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-17 14:01:33.884993
162	7	查看公告详情	查看公告: 额三反五反 (ID: 4) (IP: 172.19.0.1)	2025-12-17 14:07:07.836901
163	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-17 14:07:47.257183
164	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-17 14:11:06.871738
165	7	查看公告详情	查看公告: 额三反五反 (ID: 4) (IP: 172.19.0.1)	2025-12-17 14:11:11.388541
166	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-17 14:12:18.269547
167	7	查看公告详情	查看公告: 额三反五反 (ID: 4) (IP: 172.19.0.1)	2025-12-17 14:12:21.943956
168	7	查看公告详情	查看公告: 额三反五反 (ID: 4) (IP: 172.19.0.1)	2025-12-17 14:13:22.802095
169	7	查看公告详情	查看公告: 骨灰盒 (ID: 6) (IP: 172.19.0.1)	2025-12-17 14:15:03.640862
170	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-17 14:15:05.842965
171	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-17 14:15:09.889952
172	7	查看公告详情	查看公告: 骨灰盒 (ID: 6) (IP: 172.19.0.1)	2025-12-17 15:01:35.726214
173	8	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-18 16:47:47.782662
174	8	查看公告详情	查看公告: 骨灰盒 (ID: 6) (IP: 172.19.0.1)	2025-12-18 16:47:52.235801
175	8	用户登出	用户 陈松 登出系统	2025-12-18 16:48:17.921212
176	7	查看公告详情	查看公告: 骨灰盒 (ID: 6) (IP: 172.19.0.1)	2025-12-19 08:49:21.401548
177	7	查看公告详情	查看公告: 骨灰盒 (ID: 6) (IP: 172.19.0.1)	2025-12-19 08:51:01.611998
178	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-19 08:51:05.403093
179	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 08:51:06.323372
180	7	创建公告	创建公告: 2025n1219 (ID: 7) (IP: 172.19.0.1)	2025-12-19 08:51:41.706477
181	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 08:51:41.719267
182	7	查看公告详情	查看公告: 2025n1219 (ID: 7) (IP: 172.19.0.1)	2025-12-19 08:51:49.925746
183	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-19 08:51:58.039044
184	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 08:52:02.318211
185	7	取消发布公告	已取消发布: 2025n1219 (ID: 7) (IP: 172.19.0.1)	2025-12-19 08:52:07.920256
186	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 08:52:09.526814
187	7	编辑公告	编辑公告: 2025n1219 (ID: 7) (IP: 172.19.0.1)	2025-12-19 08:52:40.267799
188	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 08:52:40.278608
189	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 08:52:59.435434
190	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 08:53:51.309912
191	7	查看公告详情	查看公告: 2025n1219 (ID: 7) (IP: 172.19.0.1)	2025-12-19 08:53:54.372153
192	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 08:53:58.257215
193	7	访问页面	设备列表 (IP: 172.19.0.1)	2025-12-19 08:55:48.825134
194	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-19 09:03:55.665577
195	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 09:03:56.476047
196	7	创建公告	创建公告: 分发 (ID: 8) (IP: 172.19.0.1)	2025-12-19 09:05:35.707666
197	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 09:05:35.720096
198	7	查看公告详情	查看公告: 分发 (ID: 8) (IP: 172.19.0.1)	2025-12-19 09:05:38.64987
199	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-19 09:05:41.365959
200	7	查看公告详情	查看公告: 分发 (ID: 8) (IP: 172.19.0.1)	2025-12-19 09:05:48.923723
201	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-19 09:05:54.813702
202	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 09:05:56.732555
203	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-19 09:06:36.654819
204	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 09:06:37.339419
205	7	查看公告详情	查看公告: 2025n1219 (ID: 7) (IP: 172.19.0.1)	2025-12-19 09:07:36.813837
206	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-19 09:07:38.999089
207	7	查看公告详情	查看公告: 分发 (ID: 8) (IP: 172.19.0.1)	2025-12-19 09:07:40.478476
208	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-19 09:07:43.725292
209	7	访问页面	资产/配件管理中心 (IP: 172.19.0.1)	2025-12-19 09:07:46.774277
210	7	查看公告详情	查看公告: 分发 (ID: 8) (IP: 172.19.0.1)	2025-12-19 09:27:40.3693
211	7	查看公告详情	查看公告: 2025n1219 (ID: 7) (IP: 172.19.0.1)	2025-12-19 09:27:40.377763
212	7	查看公告详情	查看公告: 2025n1219 (ID: 7) (IP: 172.19.0.1)	2025-12-19 09:35:59.436663
213	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-19 09:36:05.727621
214	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 09:36:06.610007
215	7	创建公告	创建公告: 啊的方法 (ID: 9) (IP: 172.19.0.1)	2025-12-19 09:36:14.18955
216	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 09:36:16.284004
217	7	删除公告	删除公告: 2025n1219 (ID: 7) (IP: 172.19.0.1)	2025-12-19 09:36:24.080136
218	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 09:36:25.298874
219	7	查看公告详情	查看公告: 啊的方法 (ID: 9) (IP: 172.19.0.1)	2025-12-19 09:36:27.736056
220	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-19 09:36:29.742505
221	7	查看公告详情	查看公告: 用 (ID: 5) (IP: 172.19.0.1)	2025-12-19 09:36:32.559652
222	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-19 09:36:33.893323
223	7	查看公告详情	查看公告: 分发 (ID: 8) (IP: 172.19.0.1)	2025-12-19 09:36:34.735833
224	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-19 09:36:38.397554
225	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 09:36:39.16909
226	7	删除公告	删除公告: 啊的方法 (ID: 9) (IP: 172.19.0.1)	2025-12-19 09:36:41.45834
227	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 09:36:42.512018
228	7	删除公告	删除公告: 分发 (ID: 8) (IP: 172.19.0.1)	2025-12-19 09:36:44.51424
229	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 09:36:45.227754
230	7	删除公告	删除公告: 骨灰盒 (ID: 6) (IP: 172.19.0.1)	2025-12-19 09:36:47.209295
231	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 09:36:48.077991
232	7	删除公告	删除公告: 用 (ID: 5) (IP: 172.19.0.1)	2025-12-19 09:36:49.866895
233	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 09:36:50.462201
234	7	删除公告	删除公告: 额三反五反 (ID: 4) (IP: 172.19.0.1)	2025-12-19 09:36:52.083902
235	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 09:36:53.142457
236	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 10:45:27.640597
237	7	创建公告	创建公告: 测试 (ID: 10) (IP: 172.19.0.1)	2025-12-19 10:46:06.851117
238	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 10:46:09.083104
239	7	查看公告详情	查看公告: 测试 (ID: 10) (IP: 172.19.0.1)	2025-12-19 10:46:11.693893
240	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-19 10:46:13.290376
241	7	查看公告详情	查看公告: 测试 (ID: 10) (IP: 172.19.0.1)	2025-12-19 10:47:51.271283
242	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 10:47:57.547905
243	7	编辑公告	编辑公告: 测试 (ID: 10) (IP: 172.19.0.1)	2025-12-19 10:48:08.740384
244	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 10:48:10.886698
245	7	查看公告详情	查看公告: 测试 (ID: 10) (IP: 172.19.0.1)	2025-12-19 10:48:13.278146
246	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-19 10:48:15.154613
247	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-19 11:25:20.90215
248	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 11:25:22.213245
249	7	查看公告详情	查看公告: 测试 (ID: 10) (IP: 172.19.0.1)	2025-12-19 11:25:36.663803
250	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 11:25:41.937033
251	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 11:25:43.371644
252	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-19 11:25:46.698463
253	7	查看公告详情	查看公告: 测试 (ID: 10) (IP: 172.19.0.1)	2025-12-19 11:25:48.065892
254	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-19 11:25:50.072341
255	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 11:25:54.230554
256	7	删除公告	删除公告: 测试 (ID: 10) (IP: 172.19.0.1)	2025-12-19 11:25:57.347279
257	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 11:25:58.430654
258	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 17:50:36.950521
259	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 17:51:34.605071
260	7	创建公告	创建公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-19 17:51:45.907027
261	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 17:51:48.605227
262	7	查看公告详情	查看公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-19 17:51:56.053991
263	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-19 17:51:59.443751
264	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 17:52:00.850428
265	7	编辑公告	编辑公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-19 17:52:11.888329
266	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-19 17:52:13.866067
267	7	查看公告详情	查看公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-19 17:52:15.444864
268	7	查看公告详情	查看公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 07:52:34.158759
269	7	查看公告详情	查看公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 07:53:35.09476
270	7	编辑公告	编辑公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 07:53:56.663323
271	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-20 07:53:59.457245
272	7	查看公告详情	查看公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 07:54:03.412928
273	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-20 07:54:05.981618
274	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-20 07:54:31.534478
275	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-20 07:54:31.757856
276	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-20 07:54:31.960309
277	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-20 07:54:32.119045
278	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-20 07:54:32.299128
279	7	查看公告详情	查看公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 07:54:33.181377
280	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-20 07:54:51.466355
281	7	查看公告详情	查看公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 07:58:20.813963
282	7	编辑公告	编辑公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 07:58:32.369921
283	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-20 07:58:34.83199
284	7	查看公告详情	查看公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 07:58:36.665402
285	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-20 07:58:38.66499
286	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-20 07:58:40.54166
287	7	查看公告详情	查看公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 07:58:42.711312
288	7	查看公告详情	查看公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 07:58:45.596031
289	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-20 08:36:18.026941
290	7	查看公告详情	查看公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 08:36:19.439329
291	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-20 08:36:20.842867
292	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-20 08:36:23.029172
293	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-20 08:39:45.257141
294	7	查看公告详情	查看公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 08:39:46.276703
295	7	编辑公告	编辑公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 08:39:52.508991
296	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-20 08:39:54.413166
297	7	查看公告详情	查看公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 08:39:57.919309
298	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-20 08:41:26.706942
299	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-20 08:41:27.736577
300	7	编辑公告	编辑公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 08:41:33.500636
301	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-20 08:41:35.704375
302	7	查看公告详情	查看公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 08:41:38.710868
303	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-20 08:41:39.77863
304	7	查看公告详情	查看公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 08:45:55.392757
305	7	查看公告详情	查看公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 08:46:01.246933
306	7	编辑公告	编辑公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 08:46:06.995802
307	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-20 08:46:08.743597
308	7	查看公告详情	查看公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 08:46:11.493938
309	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-20 08:59:37.236788
310	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-20 08:59:38.145654
311	7	编辑公告	编辑公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 08:59:45.382946
312	7	查看公告详情	查看公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 08:59:47.441324
313	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-20 08:59:50.277798
314	7	创建角色	创建自定义角色: 部门主管 (IP: 172.19.0.1)	2025-12-20 09:07:54.05964
315	7	配置权限	配置角色"部门主管"的权限 (IP: 172.19.0.1)	2025-12-20 09:08:28.497931
316	7	分配角色	为角色"部门主管"分配了1个用户: 陈松 (IP: 172.19.0.1)	2025-12-20 09:08:33.914461
317	7	访问页面	资产/配件管理中心 (IP: 172.19.0.1)	2025-12-20 09:10:37.420236
318	7	访问页面	设备列表 (IP: 172.19.0.1)	2025-12-20 09:10:39.730286
319	7	打印标签	equipment#2 (IP: 172.19.0.1)	2025-12-20 09:10:41.36626
320	7	访问页面	部门管理 (IP: 172.19.0.1)	2025-12-20 09:11:14.994594
321	7	查看公告详情	查看公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 15:23:24.892469
322	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-20 15:23:27.098079
323	7	查看公告详情	查看公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 16:28:04.403417
324	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-20 16:28:06.47159
325	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-20 17:18:44.798415
326	7	查看公告详情	查看公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 17:18:46.233047
327	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-20 17:18:48.874422
328	7	用户登出	用户 admin 登出系统	2025-12-20 18:35:51.706325
329	8	用户登出	用户 陈松 登出系统	2025-12-20 18:36:27.444862
330	7	用户登出	用户 admin 登出系统	2025-12-20 18:49:30.752198
331	8	用户登出	用户 陈松 登出系统	2025-12-20 18:51:08.804169
332	7	查看公告详情	查看公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 18:51:17.879276
333	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-20 18:51:50.253172
334	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-20 18:51:51.444547
335	7	查看公告	访问系统公告列表 (IP: 172.19.0.1)	2025-12-20 19:27:50.914321
336	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-20 19:27:53.078105
337	7	删除公告	删除公告: 问题 (ID: 11) (IP: 172.19.0.1)	2025-12-20 19:27:56.162742
338	7	管理公告	访问公告管理页面 (IP: 172.19.0.1)	2025-12-20 19:27:57.424935
339	7	访问页面	设备列表 (IP: 172.19.0.1)	2025-12-22 08:08:25.131882
340	7	访问页面	设备列表 (IP: 172.19.0.1)	2025-12-22 08:08:39.928563
341	7	更新设备	更新设备 激光打印机001#2 (IP: 172.19.0.1)	2025-12-22 08:08:54.047416
342	7	访问页面	设备列表 (IP: 172.19.0.1)	2025-12-22 08:08:54.062946
\.


--
-- Data for Name: user_approval_role; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_approval_role (id, user_id, role_id, assigned_by_id, assigned_date, start_date, end_date, is_active, notes) FROM stdin;
\.


--
-- Data for Name: user_custom_role; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_custom_role (user_id, role_id, assigned_by_id, assigned_date, expired_date, is_active, notes) FROM stdin;
8	1	7	2025-12-20 09:08:33.910646	\N	t	\N
\.


--
-- Data for Name: workflow_instance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.workflow_instance (id, template_id, order_type, order_id, current_node_id, status, started_at, finished_at) FROM stdin;
\.


--
-- Data for Name: workflow_node; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.workflow_node (id, template_id, code, name, sequence, node_type, approval_role_id, approver_user_ids, condition_expr, amount_threshold, skip_if_below_threshold, is_parallel, required_approvals, parallel_mode, timeout_hours, timeout_action, escalate_to_role_id, auto_approve_rules, auto_reject_rules, notify_on_start, notify_on_complete, notify_methods, is_active, approver_user_id, actions_on_reject, condition_expression, parallel_count, escalate_to_user_id, role_required_name) FROM stdin;
4	3	admin_approval_2	管理员审批	2	approval	\N	\N	\N	\N	f	f	1	\N	\N	\N	\N	\N	\N	t	t	\N	t	\N	\N	\N	\N	\N	\N
3	3	leader_approval_1	部门领导审批	1	approval	1	\N	\N	\N	f	f	1	\N	\N	\N	\N	\N	\N	t	t	\N	t	\N	\N	\N	\N	\N	\N
\.


--
-- Data for Name: workflow_template; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.workflow_template (id, code, name, order_type, version, is_active, is_default, description, config, created_by_id, created_date, updated_date) FROM stdin;
3	default	默认流程模板	default_order	1	t	t	系统自动创建的默认流程模板	\N	\N	2025-12-16 02:34:49.546357	\N
\.


--
-- Name: account_request_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.account_request_id_seq', 1, false);


--
-- Name: action_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.action_log_id_seq', 1, false);


--
-- Name: announcement_attachment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.announcement_attachment_id_seq', 1, false);


--
-- Name: announcements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.announcements_id_seq', 11, true);


--
-- Name: app_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.app_user_id_seq', 8, true);


--
-- Name: approval_decision_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.approval_decision_id_seq', 1, false);


--
-- Name: approval_delegate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.approval_delegate_id_seq', 1, false);


--
-- Name: approval_instance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.approval_instance_id_seq', 6, true);


--
-- Name: approval_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.approval_log_id_seq', 24, true);


--
-- Name: approval_reminder_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.approval_reminder_id_seq', 1, false);


--
-- Name: approval_role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.approval_role_id_seq', 6, true);


--
-- Name: approval_step_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.approval_step_id_seq', 1, false);


--
-- Name: approval_workflow_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.approval_workflow_id_seq', 1, false);


--
-- Name: asset_cost_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.asset_cost_id_seq', 1, false);


--
-- Name: asset_handover_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.asset_handover_id_seq', 1, false);


--
-- Name: asset_lifecycle_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.asset_lifecycle_id_seq', 1, false);


--
-- Name: audit_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.audit_log_id_seq', 1, false);


--
-- Name: chat_attachment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.chat_attachment_id_seq', 14, true);


--
-- Name: chat_conversation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.chat_conversation_id_seq', 3, true);


--
-- Name: chat_message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.chat_message_id_seq', 35, true);


--
-- Name: chat_participant_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.chat_participant_id_seq', 5, true);


--
-- Name: chat_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.chat_permission_id_seq', 1, false);


--
-- Name: department_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.department_id_seq', 6, true);


--
-- Name: equipment_application_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.equipment_application_id_seq', 1, false);


--
-- Name: equipment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.equipment_id_seq', 3, true);


--
-- Name: equipment_loan_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.equipment_loan_id_seq', 1, false);


--
-- Name: equipment_scrap_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.equipment_scrap_id_seq', 1, false);


--
-- Name: equipment_transfer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.equipment_transfer_id_seq', 1, false);


--
-- Name: equipment_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.equipment_type_id_seq', 7, true);


--
-- Name: inventory_warning_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.inventory_warning_id_seq', 1, false);


--
-- Name: maintenance_plan_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.maintenance_plan_id_seq', 1, false);


--
-- Name: maintenance_record_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.maintenance_record_id_seq', 1, false);


--
-- Name: notification_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notification_id_seq', 1, false);


--
-- Name: part_replacement_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.part_replacement_id_seq', 1, false);


--
-- Name: part_request_order_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.part_request_order_id_seq', 1, false);


--
-- Name: permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.permission_id_seq', 10, true);


--
-- Name: repair_order_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.repair_order_id_seq', 1, false);


--
-- Name: role_definition_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.role_definition_id_seq', 1, true);


--
-- Name: spare_part_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.spare_part_id_seq', 3, true);


--
-- Name: spare_part_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.spare_part_type_id_seq', 1, true);


--
-- Name: user_activity_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_activity_log_id_seq', 342, true);


--
-- Name: user_approval_role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_approval_role_id_seq', 1, false);


--
-- Name: workflow_instance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.workflow_instance_id_seq', 1, false);


--
-- Name: workflow_node_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.workflow_node_id_seq', 4, true);


--
-- Name: workflow_template_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.workflow_template_id_seq', 3, true);


--
-- Name: account_request account_request_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.account_request
    ADD CONSTRAINT account_request_pkey PRIMARY KEY (id);


--
-- Name: action_log action_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.action_log
    ADD CONSTRAINT action_log_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: announcement_attachment announcement_attachment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.announcement_attachment
    ADD CONSTRAINT announcement_attachment_pkey PRIMARY KEY (id);


--
-- Name: announcements announcements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.announcements
    ADD CONSTRAINT announcements_pkey PRIMARY KEY (id);


--
-- Name: announcements_publish_time_backup announcements_publish_time_backup_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.announcements_publish_time_backup
    ADD CONSTRAINT announcements_publish_time_backup_pkey PRIMARY KEY (id);


--
-- Name: app_user app_user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT app_user_pkey PRIMARY KEY (id);


--
-- Name: approval_decision approval_decision_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_decision
    ADD CONSTRAINT approval_decision_pkey PRIMARY KEY (id);


--
-- Name: approval_delegate approval_delegate_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_delegate
    ADD CONSTRAINT approval_delegate_pkey PRIMARY KEY (id);


--
-- Name: approval_instance approval_instance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_instance
    ADD CONSTRAINT approval_instance_pkey PRIMARY KEY (id);


--
-- Name: approval_log approval_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_log
    ADD CONSTRAINT approval_log_pkey PRIMARY KEY (id);


--
-- Name: approval_reminder approval_reminder_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_reminder
    ADD CONSTRAINT approval_reminder_pkey PRIMARY KEY (id);


--
-- Name: approval_role approval_role_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_role
    ADD CONSTRAINT approval_role_code_key UNIQUE (code);


--
-- Name: approval_role approval_role_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_role
    ADD CONSTRAINT approval_role_pkey PRIMARY KEY (id);


--
-- Name: approval_step approval_step_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_step
    ADD CONSTRAINT approval_step_pkey PRIMARY KEY (id);


--
-- Name: approval_workflow approval_workflow_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_workflow
    ADD CONSTRAINT approval_workflow_pkey PRIMARY KEY (id);


--
-- Name: asset_cost asset_cost_equipment_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_cost
    ADD CONSTRAINT asset_cost_equipment_id_key UNIQUE (equipment_id);


--
-- Name: asset_cost asset_cost_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_cost
    ADD CONSTRAINT asset_cost_pkey PRIMARY KEY (id);


--
-- Name: asset_handover asset_handover_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_handover
    ADD CONSTRAINT asset_handover_pkey PRIMARY KEY (id);


--
-- Name: asset_lifecycle asset_lifecycle_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_lifecycle
    ADD CONSTRAINT asset_lifecycle_pkey PRIMARY KEY (id);


--
-- Name: audit_log audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_pkey PRIMARY KEY (id);


--
-- Name: chat_attachment chat_attachment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_attachment
    ADD CONSTRAINT chat_attachment_pkey PRIMARY KEY (id);


--
-- Name: chat_conversation chat_conversation_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_conversation
    ADD CONSTRAINT chat_conversation_pkey PRIMARY KEY (id);


--
-- Name: chat_message chat_message_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_message
    ADD CONSTRAINT chat_message_pkey PRIMARY KEY (id);


--
-- Name: chat_participant chat_participant_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_participant
    ADD CONSTRAINT chat_participant_pkey PRIMARY KEY (id);


--
-- Name: chat_permission chat_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_permission
    ADD CONSTRAINT chat_permission_pkey PRIMARY KEY (id);


--
-- Name: department department_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.department
    ADD CONSTRAINT department_code_key UNIQUE (code);


--
-- Name: department department_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.department
    ADD CONSTRAINT department_name_key UNIQUE (name);


--
-- Name: department department_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.department
    ADD CONSTRAINT department_pkey PRIMARY KEY (id);


--
-- Name: equipment_application equipment_application_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_application
    ADD CONSTRAINT equipment_application_pkey PRIMARY KEY (id);


--
-- Name: equipment_loan equipment_loan_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_loan
    ADD CONSTRAINT equipment_loan_pkey PRIMARY KEY (id);


--
-- Name: equipment equipment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_pkey PRIMARY KEY (id);


--
-- Name: equipment_scrap equipment_scrap_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_scrap
    ADD CONSTRAINT equipment_scrap_pkey PRIMARY KEY (id);


--
-- Name: equipment equipment_serial_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_serial_number_key UNIQUE (serial_number);


--
-- Name: equipment_transfer equipment_transfer_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_transfer
    ADD CONSTRAINT equipment_transfer_pkey PRIMARY KEY (id);


--
-- Name: equipment_type equipment_type_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_type
    ADD CONSTRAINT equipment_type_name_key UNIQUE (name);


--
-- Name: equipment_type equipment_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_type
    ADD CONSTRAINT equipment_type_pkey PRIMARY KEY (id);


--
-- Name: inventory_warning inventory_warning_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory_warning
    ADD CONSTRAINT inventory_warning_pkey PRIMARY KEY (id);


--
-- Name: maintenance_plan maintenance_plan_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maintenance_plan
    ADD CONSTRAINT maintenance_plan_pkey PRIMARY KEY (id);


--
-- Name: maintenance_record maintenance_record_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maintenance_record
    ADD CONSTRAINT maintenance_record_pkey PRIMARY KEY (id);


--
-- Name: notification notification_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification
    ADD CONSTRAINT notification_pkey PRIMARY KEY (id);


--
-- Name: part_replacement part_replacement_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.part_replacement
    ADD CONSTRAINT part_replacement_pkey PRIMARY KEY (id);


--
-- Name: part_request_order part_request_order_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.part_request_order
    ADD CONSTRAINT part_request_order_pkey PRIMARY KEY (id);


--
-- Name: permission permission_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permission
    ADD CONSTRAINT permission_pkey PRIMARY KEY (id);


--
-- Name: repair_order repair_order_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.repair_order
    ADD CONSTRAINT repair_order_pkey PRIMARY KEY (id);


--
-- Name: role_definition role_definition_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_definition
    ADD CONSTRAINT role_definition_name_key UNIQUE (name);


--
-- Name: role_definition role_definition_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_definition
    ADD CONSTRAINT role_definition_pkey PRIMARY KEY (id);


--
-- Name: spare_part spare_part_part_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.spare_part
    ADD CONSTRAINT spare_part_part_number_key UNIQUE (part_number);


--
-- Name: spare_part spare_part_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.spare_part
    ADD CONSTRAINT spare_part_pkey PRIMARY KEY (id);


--
-- Name: spare_part_type spare_part_type_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.spare_part_type
    ADD CONSTRAINT spare_part_type_name_key UNIQUE (name);


--
-- Name: spare_part_type spare_part_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.spare_part_type
    ADD CONSTRAINT spare_part_type_pkey PRIMARY KEY (id);


--
-- Name: user_activity_log user_activity_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_activity_log
    ADD CONSTRAINT user_activity_log_pkey PRIMARY KEY (id);


--
-- Name: user_approval_role user_approval_role_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_approval_role
    ADD CONSTRAINT user_approval_role_pkey PRIMARY KEY (id);


--
-- Name: user_custom_role user_custom_role_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_custom_role
    ADD CONSTRAINT user_custom_role_pkey PRIMARY KEY (user_id, role_id);


--
-- Name: workflow_instance workflow_instance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_instance
    ADD CONSTRAINT workflow_instance_pkey PRIMARY KEY (id);


--
-- Name: workflow_node workflow_node_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_node
    ADD CONSTRAINT workflow_node_pkey PRIMARY KEY (id);


--
-- Name: workflow_template workflow_template_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_template
    ADD CONSTRAINT workflow_template_pkey PRIMARY KEY (id);


--
-- Name: ix_account_request_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_account_request_username ON public.account_request USING btree (username);


--
-- Name: ix_app_user_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_app_user_email ON public.app_user USING btree (email);


--
-- Name: ix_app_user_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_app_user_username ON public.app_user USING btree (username);


--
-- Name: ix_approval_instance_instance_no; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_approval_instance_instance_no ON public.approval_instance USING btree (instance_no);


--
-- Name: ix_approval_instance_order_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_approval_instance_order_id ON public.approval_instance USING btree (order_id);


--
-- Name: ix_approval_instance_order_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_approval_instance_order_type ON public.approval_instance USING btree (order_type);


--
-- Name: ix_approval_instance_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_approval_instance_status ON public.approval_instance USING btree (status);


--
-- Name: ix_approval_log_created_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_approval_log_created_date ON public.approval_log USING btree (created_date);


--
-- Name: ix_approval_log_instance_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_approval_log_instance_id ON public.approval_log USING btree (instance_id);


--
-- Name: ix_approval_log_step_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_approval_log_step_id ON public.approval_log USING btree (step_id);


--
-- Name: ix_approval_step_instance_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_approval_step_instance_id ON public.approval_step USING btree (instance_id);


--
-- Name: ix_approval_step_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_approval_step_status ON public.approval_step USING btree (status);


--
-- Name: ix_chat_message_created_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_chat_message_created_date ON public.chat_message USING btree (created_date);


--
-- Name: ix_equipment_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_equipment_name ON public.equipment USING btree (name);


--
-- Name: ix_spare_part_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_spare_part_name ON public.spare_part USING btree (name);


--
-- Name: ix_workflow_template_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_workflow_template_code ON public.workflow_template USING btree (code);


--
-- Name: ix_workflow_template_order_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_template_order_type ON public.workflow_template USING btree (order_type);


--
-- Name: account_request account_request_approver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.account_request
    ADD CONSTRAINT account_request_approver_id_fkey FOREIGN KEY (approver_id) REFERENCES public.app_user(id);


--
-- Name: announcement_attachment announcement_attachment_announcement_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.announcement_attachment
    ADD CONSTRAINT announcement_attachment_announcement_id_fkey FOREIGN KEY (announcement_id) REFERENCES public.announcements(id);


--
-- Name: announcement_attachment announcement_attachment_upload_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.announcement_attachment
    ADD CONSTRAINT announcement_attachment_upload_user_id_fkey FOREIGN KEY (upload_user_id) REFERENCES public.app_user(id);


--
-- Name: announcements announcements_creator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.announcements
    ADD CONSTRAINT announcements_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES public.app_user(id);


--
-- Name: app_user app_user_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT app_user_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.department(id);


--
-- Name: approval_decision approval_decision_approval_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_decision
    ADD CONSTRAINT approval_decision_approval_workflow_id_fkey FOREIGN KEY (approval_workflow_id) REFERENCES public.approval_workflow(id);


--
-- Name: approval_decision approval_decision_approver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_decision
    ADD CONSTRAINT approval_decision_approver_id_fkey FOREIGN KEY (approver_id) REFERENCES public.app_user(id);


--
-- Name: approval_delegate approval_delegate_delegate_to_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_delegate
    ADD CONSTRAINT approval_delegate_delegate_to_id_fkey FOREIGN KEY (delegate_to_id) REFERENCES public.app_user(id);


--
-- Name: approval_delegate approval_delegate_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_delegate
    ADD CONSTRAINT approval_delegate_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.app_user(id);


--
-- Name: approval_instance approval_instance_current_node_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_instance
    ADD CONSTRAINT approval_instance_current_node_id_fkey FOREIGN KEY (current_node_id) REFERENCES public.workflow_node(id);


--
-- Name: approval_instance approval_instance_requester_dept_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_instance
    ADD CONSTRAINT approval_instance_requester_dept_id_fkey FOREIGN KEY (requester_dept_id) REFERENCES public.department(id);


--
-- Name: approval_instance approval_instance_requester_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_instance
    ADD CONSTRAINT approval_instance_requester_id_fkey FOREIGN KEY (requester_id) REFERENCES public.app_user(id);


--
-- Name: approval_instance approval_instance_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_instance
    ADD CONSTRAINT approval_instance_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.workflow_template(id);


--
-- Name: approval_log approval_log_instance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_log
    ADD CONSTRAINT approval_log_instance_id_fkey FOREIGN KEY (instance_id) REFERENCES public.approval_instance(id);


--
-- Name: approval_log approval_log_operator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_log
    ADD CONSTRAINT approval_log_operator_id_fkey FOREIGN KEY (operator_id) REFERENCES public.app_user(id);


--
-- Name: approval_log approval_log_step_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_log
    ADD CONSTRAINT approval_log_step_id_fkey FOREIGN KEY (step_id) REFERENCES public.approval_step(id);


--
-- Name: approval_reminder approval_reminder_sent_to_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_reminder
    ADD CONSTRAINT approval_reminder_sent_to_id_fkey FOREIGN KEY (sent_to_id) REFERENCES public.app_user(id);


--
-- Name: approval_reminder approval_reminder_step_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_reminder
    ADD CONSTRAINT approval_reminder_step_id_fkey FOREIGN KEY (step_id) REFERENCES public.approval_step(id);


--
-- Name: approval_role approval_role_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_role
    ADD CONSTRAINT approval_role_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.app_user(id);


--
-- Name: approval_step approval_step_admin_operator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_step
    ADD CONSTRAINT approval_step_admin_operator_id_fkey FOREIGN KEY (admin_operator_id) REFERENCES public.app_user(id);


--
-- Name: approval_step approval_step_approver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_step
    ADD CONSTRAINT approval_step_approver_id_fkey FOREIGN KEY (approver_id) REFERENCES public.app_user(id);


--
-- Name: approval_step approval_step_approver_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_step
    ADD CONSTRAINT approval_step_approver_role_id_fkey FOREIGN KEY (approver_role_id) REFERENCES public.approval_role(id);


--
-- Name: approval_step approval_step_instance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_step
    ADD CONSTRAINT approval_step_instance_id_fkey FOREIGN KEY (instance_id) REFERENCES public.approval_instance(id);


--
-- Name: approval_step approval_step_node_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_step
    ADD CONSTRAINT approval_step_node_id_fkey FOREIGN KEY (node_id) REFERENCES public.workflow_node(id);


--
-- Name: approval_step approval_step_transferred_from_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_step
    ADD CONSTRAINT approval_step_transferred_from_id_fkey FOREIGN KEY (transferred_from_id) REFERENCES public.app_user(id);


--
-- Name: approval_step approval_step_transferred_to_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_step
    ADD CONSTRAINT approval_step_transferred_to_id_fkey FOREIGN KEY (transferred_to_id) REFERENCES public.app_user(id);


--
-- Name: approval_workflow approval_workflow_admin_operator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_workflow
    ADD CONSTRAINT approval_workflow_admin_operator_id_fkey FOREIGN KEY (admin_operator_id) REFERENCES public.app_user(id);


--
-- Name: approval_workflow approval_workflow_approver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_workflow
    ADD CONSTRAINT approval_workflow_approver_id_fkey FOREIGN KEY (approver_id) REFERENCES public.app_user(id);


--
-- Name: approval_workflow approval_workflow_node_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_workflow
    ADD CONSTRAINT approval_workflow_node_id_fkey FOREIGN KEY (node_id) REFERENCES public.workflow_node(id);


--
-- Name: approval_workflow approval_workflow_transferred_from_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_workflow
    ADD CONSTRAINT approval_workflow_transferred_from_id_fkey FOREIGN KEY (transferred_from_id) REFERENCES public.app_user(id);


--
-- Name: asset_cost asset_cost_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_cost
    ADD CONSTRAINT asset_cost_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(id);


--
-- Name: asset_handover asset_handover_completed_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_handover
    ADD CONSTRAINT asset_handover_completed_by_id_fkey FOREIGN KEY (completed_by_id) REFERENCES public.app_user(id);


--
-- Name: asset_handover asset_handover_from_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_handover
    ADD CONSTRAINT asset_handover_from_user_id_fkey FOREIGN KEY (from_user_id) REFERENCES public.app_user(id);


--
-- Name: asset_handover asset_handover_to_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_handover
    ADD CONSTRAINT asset_handover_to_user_id_fkey FOREIGN KEY (to_user_id) REFERENCES public.app_user(id);


--
-- Name: asset_lifecycle asset_lifecycle_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_lifecycle
    ADD CONSTRAINT asset_lifecycle_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(id);


--
-- Name: asset_lifecycle asset_lifecycle_responsible_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_lifecycle
    ADD CONSTRAINT asset_lifecycle_responsible_user_id_fkey FOREIGN KEY (responsible_user_id) REFERENCES public.app_user(id);


--
-- Name: audit_log audit_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.app_user(id);


--
-- Name: chat_attachment chat_attachment_message_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_attachment
    ADD CONSTRAINT chat_attachment_message_id_fkey FOREIGN KEY (message_id) REFERENCES public.chat_message(id);


--
-- Name: chat_conversation chat_conversation_creator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_conversation
    ADD CONSTRAINT chat_conversation_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES public.app_user(id);


--
-- Name: chat_conversation chat_conversation_last_message_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_conversation
    ADD CONSTRAINT chat_conversation_last_message_id_fkey FOREIGN KEY (last_message_id) REFERENCES public.chat_message(id);


--
-- Name: chat_message chat_message_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_message
    ADD CONSTRAINT chat_message_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.chat_conversation(id);


--
-- Name: chat_message chat_message_reply_to_message_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_message
    ADD CONSTRAINT chat_message_reply_to_message_id_fkey FOREIGN KEY (reply_to_message_id) REFERENCES public.chat_message(id);


--
-- Name: chat_message chat_message_sender_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_message
    ADD CONSTRAINT chat_message_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.app_user(id);


--
-- Name: chat_participant chat_participant_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_participant
    ADD CONSTRAINT chat_participant_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.chat_conversation(id);


--
-- Name: chat_participant chat_participant_last_read_message_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_participant
    ADD CONSTRAINT chat_participant_last_read_message_id_fkey FOREIGN KEY (last_read_message_id) REFERENCES public.chat_message(id);


--
-- Name: chat_participant chat_participant_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_participant
    ADD CONSTRAINT chat_participant_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.app_user(id);


--
-- Name: chat_permission chat_permission_operated_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_permission
    ADD CONSTRAINT chat_permission_operated_by_id_fkey FOREIGN KEY (operated_by_id) REFERENCES public.app_user(id);


--
-- Name: chat_permission chat_permission_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_permission
    ADD CONSTRAINT chat_permission_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.app_user(id);


--
-- Name: equipment_application equipment_application_applicant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_application
    ADD CONSTRAINT equipment_application_applicant_id_fkey FOREIGN KEY (applicant_id) REFERENCES public.app_user(id);


--
-- Name: equipment_application equipment_application_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_application
    ADD CONSTRAINT equipment_application_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(id);


--
-- Name: equipment equipment_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.department(id);


--
-- Name: equipment_loan equipment_loan_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_loan
    ADD CONSTRAINT equipment_loan_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.app_user(id);


--
-- Name: equipment_loan equipment_loan_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_loan
    ADD CONSTRAINT equipment_loan_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(id);


--
-- Name: equipment_loan equipment_loan_inspected_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_loan
    ADD CONSTRAINT equipment_loan_inspected_by_fkey FOREIGN KEY (inspected_by) REFERENCES public.app_user(id);


--
-- Name: equipment_loan equipment_loan_requester_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_loan
    ADD CONSTRAINT equipment_loan_requester_id_fkey FOREIGN KEY (requester_id) REFERENCES public.app_user(id);


--
-- Name: equipment_scrap equipment_scrap_disposal_handler_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_scrap
    ADD CONSTRAINT equipment_scrap_disposal_handler_fkey FOREIGN KEY (disposal_handler) REFERENCES public.app_user(id);


--
-- Name: equipment_scrap equipment_scrap_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_scrap
    ADD CONSTRAINT equipment_scrap_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(id);


--
-- Name: equipment_scrap equipment_scrap_financial_cleared_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_scrap
    ADD CONSTRAINT equipment_scrap_financial_cleared_by_fkey FOREIGN KEY (financial_cleared_by) REFERENCES public.app_user(id);


--
-- Name: equipment_scrap equipment_scrap_requester_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_scrap
    ADD CONSTRAINT equipment_scrap_requester_id_fkey FOREIGN KEY (requester_id) REFERENCES public.app_user(id);


--
-- Name: equipment_transfer equipment_transfer_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_transfer
    ADD CONSTRAINT equipment_transfer_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(id);


--
-- Name: equipment_transfer equipment_transfer_requester_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment_transfer
    ADD CONSTRAINT equipment_transfer_requester_id_fkey FOREIGN KEY (requester_id) REFERENCES public.app_user(id);


--
-- Name: equipment equipment_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.equipment_type(id);


--
-- Name: chat_attachment fk_chat_attachment_message; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_attachment
    ADD CONSTRAINT fk_chat_attachment_message FOREIGN KEY (message_id) REFERENCES public.chat_message(id);


--
-- Name: chat_conversation fk_chat_conversation_creator; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_conversation
    ADD CONSTRAINT fk_chat_conversation_creator FOREIGN KEY (creator_id) REFERENCES public.app_user(id);


--
-- Name: chat_conversation fk_chat_conversation_last_message; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_conversation
    ADD CONSTRAINT fk_chat_conversation_last_message FOREIGN KEY (last_message_id) REFERENCES public.chat_message(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: chat_message fk_chat_message_conversation; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_message
    ADD CONSTRAINT fk_chat_message_conversation FOREIGN KEY (conversation_id) REFERENCES public.chat_conversation(id);


--
-- Name: chat_message fk_chat_message_reply_to; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_message
    ADD CONSTRAINT fk_chat_message_reply_to FOREIGN KEY (reply_to_message_id) REFERENCES public.chat_message(id);


--
-- Name: chat_message fk_chat_message_sender; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_message
    ADD CONSTRAINT fk_chat_message_sender FOREIGN KEY (sender_id) REFERENCES public.app_user(id);


--
-- Name: chat_participant fk_chat_participant_conversation; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_participant
    ADD CONSTRAINT fk_chat_participant_conversation FOREIGN KEY (conversation_id) REFERENCES public.chat_conversation(id);


--
-- Name: chat_participant fk_chat_participant_last_read; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_participant
    ADD CONSTRAINT fk_chat_participant_last_read FOREIGN KEY (last_read_message_id) REFERENCES public.chat_message(id);


--
-- Name: chat_participant fk_chat_participant_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_participant
    ADD CONSTRAINT fk_chat_participant_user FOREIGN KEY (user_id) REFERENCES public.app_user(id);


--
-- Name: chat_permission fk_chat_permission_operated_by; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_permission
    ADD CONSTRAINT fk_chat_permission_operated_by FOREIGN KEY (operated_by_id) REFERENCES public.app_user(id);


--
-- Name: chat_permission fk_chat_permission_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_permission
    ADD CONSTRAINT fk_chat_permission_user FOREIGN KEY (user_id) REFERENCES public.app_user(id);


--
-- Name: inventory_warning inventory_warning_spare_part_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory_warning
    ADD CONSTRAINT inventory_warning_spare_part_id_fkey FOREIGN KEY (spare_part_id) REFERENCES public.spare_part(id);


--
-- Name: maintenance_plan maintenance_plan_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maintenance_plan
    ADD CONSTRAINT maintenance_plan_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.app_user(id);


--
-- Name: maintenance_plan maintenance_plan_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maintenance_plan
    ADD CONSTRAINT maintenance_plan_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(id);


--
-- Name: maintenance_plan maintenance_plan_responsible_person_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maintenance_plan
    ADD CONSTRAINT maintenance_plan_responsible_person_fkey FOREIGN KEY (responsible_person) REFERENCES public.app_user(id);


--
-- Name: maintenance_record maintenance_record_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maintenance_record
    ADD CONSTRAINT maintenance_record_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(id);


--
-- Name: maintenance_record maintenance_record_performed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maintenance_record
    ADD CONSTRAINT maintenance_record_performed_by_fkey FOREIGN KEY (performed_by) REFERENCES public.app_user(id);


--
-- Name: maintenance_record maintenance_record_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maintenance_record
    ADD CONSTRAINT maintenance_record_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.maintenance_plan(id);


--
-- Name: notification notification_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification
    ADD CONSTRAINT notification_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.app_user(id);


--
-- Name: part_replacement part_replacement_repair_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.part_replacement
    ADD CONSTRAINT part_replacement_repair_order_id_fkey FOREIGN KEY (repair_order_id) REFERENCES public.repair_order(id);


--
-- Name: part_replacement part_replacement_spare_part_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.part_replacement
    ADD CONSTRAINT part_replacement_spare_part_id_fkey FOREIGN KEY (spare_part_id) REFERENCES public.spare_part(id);


--
-- Name: part_request_order part_request_order_admin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.part_request_order
    ADD CONSTRAINT part_request_order_admin_id_fkey FOREIGN KEY (admin_id) REFERENCES public.app_user(id);


--
-- Name: part_request_order part_request_order_department_head_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.part_request_order
    ADD CONSTRAINT part_request_order_department_head_id_fkey FOREIGN KEY (department_head_id) REFERENCES public.app_user(id);


--
-- Name: part_request_order part_request_order_requester_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.part_request_order
    ADD CONSTRAINT part_request_order_requester_id_fkey FOREIGN KEY (requester_id) REFERENCES public.app_user(id);


--
-- Name: permission permission_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permission
    ADD CONSTRAINT permission_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.role_definition(id);


--
-- Name: repair_order repair_order_admin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.repair_order
    ADD CONSTRAINT repair_order_admin_id_fkey FOREIGN KEY (admin_id) REFERENCES public.app_user(id);


--
-- Name: repair_order repair_order_department_head_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.repair_order
    ADD CONSTRAINT repair_order_department_head_id_fkey FOREIGN KEY (department_head_id) REFERENCES public.app_user(id);


--
-- Name: repair_order repair_order_equipment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.repair_order
    ADD CONSTRAINT repair_order_equipment_id_fkey FOREIGN KEY (equipment_id) REFERENCES public.equipment(id);


--
-- Name: repair_order repair_order_requester_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.repair_order
    ADD CONSTRAINT repair_order_requester_id_fkey FOREIGN KEY (requester_id) REFERENCES public.app_user(id);


--
-- Name: repair_order repair_order_technician_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.repair_order
    ADD CONSTRAINT repair_order_technician_id_fkey FOREIGN KEY (technician_id) REFERENCES public.app_user(id);


--
-- Name: role_definition role_definition_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_definition
    ADD CONSTRAINT role_definition_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.app_user(id);


--
-- Name: spare_part spare_part_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.spare_part
    ADD CONSTRAINT spare_part_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.department(id);


--
-- Name: spare_part spare_part_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.spare_part
    ADD CONSTRAINT spare_part_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.spare_part_type(id);


--
-- Name: user_activity_log user_activity_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_activity_log
    ADD CONSTRAINT user_activity_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.app_user(id);


--
-- Name: user_approval_role user_approval_role_assigned_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_approval_role
    ADD CONSTRAINT user_approval_role_assigned_by_id_fkey FOREIGN KEY (assigned_by_id) REFERENCES public.app_user(id);


--
-- Name: user_approval_role user_approval_role_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_approval_role
    ADD CONSTRAINT user_approval_role_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.approval_role(id) ON DELETE CASCADE;


--
-- Name: user_approval_role user_approval_role_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_approval_role
    ADD CONSTRAINT user_approval_role_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.app_user(id) ON DELETE CASCADE;


--
-- Name: user_custom_role user_custom_role_assigned_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_custom_role
    ADD CONSTRAINT user_custom_role_assigned_by_id_fkey FOREIGN KEY (assigned_by_id) REFERENCES public.app_user(id);


--
-- Name: user_custom_role user_custom_role_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_custom_role
    ADD CONSTRAINT user_custom_role_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.role_definition(id) ON DELETE CASCADE;


--
-- Name: user_custom_role user_custom_role_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_custom_role
    ADD CONSTRAINT user_custom_role_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.app_user(id) ON DELETE CASCADE;


--
-- Name: workflow_instance workflow_instance_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_instance
    ADD CONSTRAINT workflow_instance_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.workflow_template(id);


--
-- Name: workflow_node workflow_node_approval_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_node
    ADD CONSTRAINT workflow_node_approval_role_id_fkey FOREIGN KEY (approval_role_id) REFERENCES public.approval_role(id);


--
-- Name: workflow_node workflow_node_escalate_to_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_node
    ADD CONSTRAINT workflow_node_escalate_to_role_id_fkey FOREIGN KEY (escalate_to_role_id) REFERENCES public.approval_role(id);


--
-- Name: workflow_node workflow_node_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_node
    ADD CONSTRAINT workflow_node_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.workflow_template(id);


--
-- Name: workflow_template workflow_template_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_template
    ADD CONSTRAINT workflow_template_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.app_user(id);


--
-- PostgreSQL database dump complete
--

\unrestrict QmBRqfimiD1UHwk4oftMij722r1nQpvjY3eiRYt1UwOyBo9h58JLPDVr7ZyH8s9

