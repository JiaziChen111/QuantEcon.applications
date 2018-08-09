#=
@author : Spencer Lyon
          Victoria Gregory

@date: 07/09/2014
=#

using Plots
pyplot()

const r = 0.05
const beta = 1.0 / (1.0 + r)
const T = 20  # Time horizon
const S = 5   # Impulse date
const sigma1 = 0.15
const sigma2 = 0.15


function time_path(permanent=false)
    w1 = zeros(T+1)
    w2 = zeros(T+1)
    b = zeros(T+1)
    c = zeros(T+1)

    if permanent === false
        w2[S+2] = 1.0
    else
        w1[S+2] = 1.0
    end

    for t=2:T
        b[t+1] = b[t] - sigma2 * w2[t]
        c[t+1] = c[t] + sigma1 * w1[t+1] + (1 - beta) * sigma2 * w2[t+1]
    end

    return b, c
end


function main()
    L = 0.175

    b1, c1 = time_path(false)
    b2, c2 = time_path(true)
    p = plot(0:T, [c1 c2 b1 b2], layout=(2, 1),
             color=[:green :green :blue :blue],
             label=["consumption" "consumption" "debt" "debt"])
    t = ["impulse-response, transitory income shock"
         "impulse-response, permanent income shock"]
    plot!(title=t', xlabel="Time", ylims=(-L, L), legend=[:topright :bottomright])
    vline!([S S], color=:black, layout=(2, 1), label="")

    return p
end
