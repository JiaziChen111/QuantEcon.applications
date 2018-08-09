#=
Agent dynamics in the lake model
=#

using QuantEcon
using Plots
pyplot()
include("lake_model.jl")

srand(42)
lm = LakeModel(d=0, b=0)
T = 5000     # Simulation length

alpha, lambda = lm.alpha, lm.lambda
P = [(1 - lambda) lambda; alpha (1 - alpha)]

mc = MarkovChain(P, [0; 1])     # 0=unemployed, 1=employed
xbar = rate_steady_state(lm)

s_path = simulate(mc, T; init=2)
s_bar_e = cumsum(s_path) ./ (1:T)
s_bar_u = 1 - s_bar_e
s_bars = [s_bar_u s_bar_e]

titles = ["Proportion of time unemployed" "Proportion of time employed"]
dates = collect(1:T)

plot(dates, s_bars, layout=(2, 1), title=titles, legend=:none)
hline!(reverse(xbar)', layout=(2, 1), color=:red, linestyle=:dash)
