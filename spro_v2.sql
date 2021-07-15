--
-- PostgreSQL database dump
--

-- Dumped from database version 12.4
-- Dumped by pg_dump version 12.4

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
-- Name: problems; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE public.problems (
    id integer NOT NULL,
    title character varying,
    text character varying,
    correct_ans character varying
);


ALTER TABLE public.problems OWNER TO root;

--
-- Name: problems_id_seq; Type: SEQUENCE; Schema: public; Owner: root
--

CREATE SEQUENCE public.problems_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.problems_id_seq OWNER TO root;

--
-- Name: problems_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: root
--

ALTER SEQUENCE public.problems_id_seq OWNED BY public.problems.id;


--
-- Name: problems id; Type: DEFAULT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.problems ALTER COLUMN id SET DEFAULT nextval('public.problems_id_seq'::regclass);


--
-- Data for Name: problems; Type: TABLE DATA; Schema: public; Owner: root
--

COPY public.problems (id, title, text, correct_ans) FROM stdin;
1	esreveR	テキストを反転して表示せよ	MzIxY2JhCg==
2	g/re/p	DISTRIB_CODENAMEの値を取り出せ	RElTVFJJQl9DT0RFTkFNRT1mb2NhbAo=
3	#	hogeという文字列を、sha256でハッシュ化せよ。ファイルは、hogeという文字列をmd5でハッシュ化したものである。	MmUwMzkwZWIwMjRhNTI5NjNkYjdiOTVlODRhOWMyYjEyYzAwNDA1NGE3YmFkOWE5N2VjMGM3Yzg5ZDQ2ODFkMgo=
\.


--
-- Name: problems_id_seq; Type: SEQUENCE SET; Schema: public; Owner: root
--

SELECT pg_catalog.setval('public.problems_id_seq', 1, false);


--
-- Name: problems problems_pkey; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.problems
    ADD CONSTRAINT problems_pkey PRIMARY KEY (id);


--
-- Name: ix_problems_correct_ans; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_problems_correct_ans ON public.problems USING btree (correct_ans);


--
-- Name: ix_problems_id; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_problems_id ON public.problems USING btree (id);


--
-- Name: ix_problems_text; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_problems_text ON public.problems USING btree (text);


--
-- Name: ix_problems_title; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_problems_title ON public.problems USING btree (title);


--
-- PostgreSQL database dump complete
--

