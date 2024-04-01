--
-- PostgreSQL database dump
--

-- Dumped from database version 15.6
-- Dumped by pg_dump version 15.6

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

--
-- Name: semantic-chunks; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA "semantic-chunks";


ALTER SCHEMA "semantic-chunks" OWNER TO postgres;

--
-- Name: semantic-search; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA "semantic-search";


ALTER SCHEMA "semantic-search" OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: chunk_table; Type: TABLE; Schema: semantic-chunks; Owner: postgres
--

CREATE TABLE "semantic-chunks".chunk_table (
    id bigint NOT NULL,
    chunk_text text,
    chunk_encoded bytea
);


ALTER TABLE "semantic-chunks".chunk_table OWNER TO postgres;

--
-- Name: chunk_table_id_seq; Type: SEQUENCE; Schema: semantic-chunks; Owner: postgres
--

CREATE SEQUENCE "semantic-chunks".chunk_table_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "semantic-chunks".chunk_table_id_seq OWNER TO postgres;

--
-- Name: chunk_table_id_seq; Type: SEQUENCE OWNED BY; Schema: semantic-chunks; Owner: postgres
--

ALTER SEQUENCE "semantic-chunks".chunk_table_id_seq OWNED BY "semantic-chunks".chunk_table.id;


--
-- Name: corpus; Type: TABLE; Schema: semantic-search; Owner: postgres
--

CREATE TABLE "semantic-search".corpus (
    id bigint NOT NULL,
    filename text,
    path text,
    process_time timestamp with time zone,
    text_extract_time_ms bigint,
    chunk_time_sec bigint,
    encode_time_sec bigint,
    file_hash text,
    faiss_indexed boolean
);


ALTER TABLE "semantic-search".corpus OWNER TO postgres;

--
-- Name: corpus_id_seq; Type: SEQUENCE; Schema: semantic-search; Owner: postgres
--

ALTER TABLE "semantic-search".corpus ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME "semantic-search".corpus_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: chunk_table id; Type: DEFAULT; Schema: semantic-chunks; Owner: postgres
--

ALTER TABLE ONLY "semantic-chunks".chunk_table ALTER COLUMN id SET DEFAULT nextval('"semantic-chunks".chunk_table_id_seq'::regclass);


--
-- Name: chunk_table chunk_table_pkey; Type: CONSTRAINT; Schema: semantic-chunks; Owner: postgres
--

ALTER TABLE ONLY "semantic-chunks".chunk_table
    ADD CONSTRAINT chunk_table_pkey PRIMARY KEY (id);


--
-- Name: corpus corpus_pkey; Type: CONSTRAINT; Schema: semantic-search; Owner: postgres
--

ALTER TABLE ONLY "semantic-search".corpus
    ADD CONSTRAINT corpus_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

