# Living-review maintenance model
# Primary R implementation. Base R only; mathematical design inputs are supplied explicitly.
# Units: all normalized burdens are dimensionless ratios to Q = D*H.

stale_fraction_exp <- function(z) {
  stopifnot(all(is.finite(z)), all(z >= 0))
  out <- numeric(length(z))
  small <- z < 1e-6
  if (any(small)) {
    zz <- z[small]
    out[small] <- zz/2 - zz^2/6 + zz^3/24 - zz^4/120 + zz^5/720
  }
  if (any(!small)) {
    zz <- z[!small]
    out[!small] <- 1 + expm1(-zz)/zz
  }
  out
}

inspection_balance_exp <- function(x) {
  stopifnot(all(is.finite(x)), all(x >= 0))
  1 - (1 + x) * exp(-x)
}

# Real Lambert W for z in [-1/e,0). This is implemented independently
# so the core model has no package dependency. branch must be 0 or -1.
lambert_w_real <- function(z, branch = 0L, tol = 5e-14, maxit = 100L) {
  if (length(z) != 1L || !is.finite(z) || z < -1/exp(1) || z >= 0)
    stop("z must be a scalar in [-1/e, 0)")
  if (!(branch %in% c(0L, -1L))) stop("branch must be 0 or -1")
  if (abs(z + 1/exp(1)) < 2e-16) return(-1)

  q <- 1 + exp(1) * z
  if (q < 0) q <- 0
  p <- sqrt(2 * q)
  if (branch == 0L) {
    w <- if (q < 0.08) -1 + p - p^2/3 + 11*p^3/72 else z
  } else {
    w <- if (q < 0.08) -1 - p - p^2/3 - 11*p^3/72 else log(-z) - log(-log(-z))
    if (w > -1) w <- -1.1
  }

  for (i in seq_len(maxit)) {
    ew <- exp(w)
    f <- w * ew - z
    wp1 <- w + 1
    if (abs(wp1) < 1e-10) {
      # Near the branch point, Newton is safer than the Halley denominator.
      step <- f / (ew * wp1 + sign(wp1) * 1e-18)
    } else {
      step <- f / (ew * wp1 - (w + 2) * f / (2 * wp1))
    }
    wnew <- w - step
    if (branch == -1L && wnew > -1) wnew <- (w - 1)/2
    if (branch == 0L && wnew < -1) wnew <- (w - 1)/2
    if (abs(wnew - w) <= tol * (1 + abs(wnew))) return(wnew)
    w <- wnew
  }
  stop("Lambert W iteration did not converge")
}

scheduled_x_lambert <- function(rho) {
  if (length(rho) != 1L || !is.finite(rho) || rho < 0) stop("rho must be nonnegative")
  if (rho == 0) return(0)
  if (rho >= 1) return(Inf)
  -1 - lambert_w_real(-(1 - rho)/exp(1), branch = -1L)
}

scheduled_x_root <- function(rho, tol = 1e-13) {
  if (length(rho) != 1L || !is.finite(rho) || rho < 0) stop("rho must be nonnegative")
  if (rho == 0) return(0)
  if (rho >= 1) return(Inf)
  hi <- max(1, sqrt(2*rho) + 1)
  while (inspection_balance_exp(hi) <= rho) hi <- 2*hi
  uniroot(function(x) inspection_balance_exp(x) - rho,
          lower = 0, upper = hi, tol = tol)$root
}

scheduled_x_star <- function(rho) {
  if (rho == 0 || rho >= 1) return(scheduled_x_root(rho))
  x <- tryCatch(scheduled_x_lambert(rho), error = function(e) NA_real_)
  if (!is.finite(x) || x <= 0 || abs(inspection_balance_exp(x) - rho) > 2e-11)
    x <- scheduled_x_root(rho)
  x
}

scheduled_min_variable <- function(rho) {
  if (length(rho) != 1L || !is.finite(rho) || rho < 0) stop("rho must be nonnegative")
  if (rho == 0) return(0)
  if (rho >= 1) return(1)
  1 - exp(-scheduled_x_star(rho))
}

scheduled_burden <- function(x, rho, c_s = 0) {
  if (!is.finite(x) || x <= 0) stop("x must be finite and positive")
  c_s + rho/x + stale_fraction_exp(x)
}

living_burden <- function(d, phi = 0, eta = 0, delta_c = 0, c_s = 0) {
  if (!is.finite(d) || d < 0) stop("d must be finite and nonnegative")
  c_s + phi + eta + delta_c + stale_fraction_exp(d)
}

living_advantage <- function(rho, d, phi = 0, eta = 0, delta_c = 0) {
  scheduled_min_variable(rho) - (phi + eta + delta_c + stale_fraction_exp(d))
}

living_dominates <- function(rho, d, phi = 0, eta = 0, delta_c = 0) {
  living_advantage(rho, d, phi, eta, delta_c) > 0
}

portfolio_break_even <- function(rho, d, alpha, F_over_Q, eta = 0, delta_c = 0) {
  if (alpha < 0 || alpha > 1 || F_over_Q < 0) stop("invalid alpha or F_over_Q")
  B <- scheduled_min_variable(rho) - stale_fraction_exp(d) - eta - delta_c
  if (B <= 0) return(Inf)
  alpha * F_over_Q / B
}

alpha_break_even <- function(rho, d, n, F_over_Q, eta = 0, delta_c = 0) {
  if (n <= 0 || F_over_Q <= 0) stop("n and F_over_Q must be positive")
  B <- scheduled_min_variable(rho) - stale_fraction_exp(d) - eta - delta_c
  if (B <= 0) return(0)
  n * B / F_over_Q
}

cadence_break_even_root <- function(rho, phi = 0, eta = 0, delta_c = 0, tol = 1e-13) {
  z <- scheduled_min_variable(rho) - phi - eta - delta_c
  if (z <= 0) return(0)
  if (z >= 1) return(Inf)
  hi <- 1
  while (stale_fraction_exp(hi) <= z) hi <- 2*hi
  uniroot(function(d) stale_fraction_exp(d) - z,
          lower = 0, upper = hi, tol = tol)$root
}

topic_rho_break_even <- function(d, phi = 0, eta = 0, delta_c = 0) {
  ctot <- stale_fraction_exp(d) + phi + eta + delta_c
  if (ctot <= 0) return(0)
  if (ctot >= 1) return(1)
  ctot + (1 - ctot) * log1p(-ctot)
}

# General survival-family helpers and required non-exponential Weibull extension.
weibull_survival <- function(x, shape) {
  if (shape <= 0 || any(x < 0)) stop("shape > 0 and x >= 0 required")
  exp(-(x^shape))
}

weibull_survival_integral <- function(x, shape) {
  if (shape <= 0 || any(x < 0)) stop("shape > 0 and x >= 0 required")
  gamma(1 + 1/shape) * pgamma(x^shape, shape = 1/shape)
}

weibull_stale_fraction <- function(x, shape) {
  if (x == 0) return(0)
  1 - weibull_survival_integral(x, shape)/x
}

weibull_characteristic <- function(x, shape) {
  weibull_survival_integral(x, shape) - x * weibull_survival(x, shape)
}

weibull_x_star <- function(rho, shape, tol = 1e-12) {
  if (rho < 0 || shape <= 0) stop("rho >= 0 and shape > 0 required")
  mean_survival <- gamma(1 + 1/shape)
  if (rho == 0) return(0)
  if (rho >= mean_survival) return(Inf)
  hi <- 1
  while (weibull_characteristic(hi, shape) <= rho) hi <- 2*hi
  uniroot(function(x) weibull_characteristic(x, shape) - rho,
          lower = 0, upper = hi, tol = tol)$root
}

weibull_min_variable <- function(rho, shape) {
  mean_survival <- gamma(1 + 1/shape)
  if (rho == 0) return(0)
  if (rho >= mean_survival) return(1)
  1 - weibull_survival(weibull_x_star(rho, shape), shape)
}
