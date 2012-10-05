%%% ----------------------------------------------------------------------------
%%% @private
%%% @author Oscar Hellström <oscar@erlang-consulting.com>
%%%
%%% @version 0.2, 2006-08-02
%%% @copyright 2006 Erlang Training and Consulting
%%%
%%% @doc
%%% @end
%%% ----------------------------------------------------------------------------
-module(agi_sup).
-behaviour(supervisor).

%%% API exports
-export([start_link/0]).

%%% supervisor callbacks
-export([init/1]).

%% -----------------------------------------------------------------------------
%% @spec start_link() -> {ok, Pid}
%% @doc
%% Starts the supervisor.
%% @end
%% -----------------------------------------------------------------------------
start_link() ->
	supervisor:start_link(?MODULE, null).

%% @hidden
init(null) ->
	{ok, Port}    = application:get_env(agi_port),
    {ok, Options} = application:get_env(agi_server_options),
	AGIServerSpec = {agi_server, {agi_server, start_link, [Port, [], Options]},
				   permanent, 1000, worker, [agi_server, agi]},
	AGIEventMgrSpec = {agi_events, {agi_events, start_link, []},
				   permanent, 1000, worker, [agi_events]},
	ChannelSupSpec = {channel_sup, {agi_channel_sup, start_link, []},
				   permanent, infinity, supervisor, [agi_channel_sup]},
	{ok, {{one_for_one, 10, 60}, [AGIServerSpec, AGIEventMgrSpec, ChannelSupSpec]}}.
