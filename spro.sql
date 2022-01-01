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
-- Name: answers; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE public.answers (
    number_of_trial integer NOT NULL,
    problem_id integer,
    username character varying,
    script character varying,
    is_correct boolean,
    result character varying
);


ALTER TABLE public.answers OWNER TO root;

--
-- Name: answers_number_of_trial_seq; Type: SEQUENCE; Schema: public; Owner: root
--

CREATE SEQUENCE public.answers_number_of_trial_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.answers_number_of_trial_seq OWNER TO root;

--
-- Name: answers_number_of_trial_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: root
--

ALTER SEQUENCE public.answers_number_of_trial_seq OWNED BY public.answers.number_of_trial;


--
-- Name: problems; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE public.problems (
    id integer NOT NULL,
    title character varying,
    text character varying,
    hint1 character varying,
    hint2 character varying,
    shell character varying,
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
-- Name: users; Type: TABLE; Schema: public; Owner: root
--


CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying,
    email character varying,
    hashed_password character varying,
    is_active boolean,
    is_superuser boolean
);


ALTER TABLE public.users OWNER TO root;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: root
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO root;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: root
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: answers number_of_trial; Type: DEFAULT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.answers ALTER COLUMN number_of_trial SET DEFAULT nextval('public.answers_number_of_trial_seq'::regclass);


--
-- Name: problems id; Type: DEFAULT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.problems ALTER COLUMN id SET DEFAULT nextval('public.problems_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: answers; Type: TABLE DATA; Schema: public; Owner: root
--

COPY public.answers (number_of_trial, problem_id, username, script, is_correct, result) FROM stdin;
\.


--
-- Data for Name: problems; Type: TABLE DATA; Schema: public; Owner: root
--

COPY public.problems (id, title, text, hint1, hint2, shell, correct_ans) FROM stdin;
1	[Tutorial]esreveR	テキストを反転して表示せよ	hint1	hint2	cat q_1.txt | rev	dc738a32870c7ee3a60e8f912a2eed3882114cc706f424838b06a58e242dbbb9
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: root
--

COPY public.users (id, username, email, hashed_password, is_active, is_superuser) FROM stdin;
\.


--
-- Name: answers_number_of_trial_seq; Type: SEQUENCE SET; Schema: public; Owner: root
--

SELECT pg_catalog.setval('public.answers_number_of_trial_seq', 1, false);


--
-- Name: problems_id_seq; Type: SEQUENCE SET; Schema: public; Owner: root
--

SELECT pg_catalog.setval('public.problems_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: root
--

SELECT pg_catalog.setval('public.users_id_seq', 1, false);


--
-- Name: answers answers_pkey; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.answers
    ADD CONSTRAINT answers_pkey PRIMARY KEY (number_of_trial);


--
-- Name: problems problems_id_key; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.problems
    ADD CONSTRAINT problems_id_key UNIQUE (id);


--
-- Name: problems problems_pkey; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.problems
    ADD CONSTRAINT problems_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_answers_number_of_trial; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_answers_number_of_trial ON public.answers USING btree (number_of_trial);


--
-- Name: ix_answers_problem_id; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_answers_problem_id ON public.answers USING btree (problem_id);



--
-- Name: ix_answers_result; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_answers_result ON public.answers USING btree (result);


--
-- Name: ix_answers_script; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_answers_script ON public.answers USING btree (script);


--
-- Name: ix_answers_username; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_answers_username ON public.answers USING btree (username);


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
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: root
--

CREATE INDEX ix_users_username ON public.users USING btree (username);


--
-- PostgreSQL database dump complete
--


