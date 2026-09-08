# Base-R test suite for the primary implementation.
script_arg <- grep("^--file=", commandArgs(FALSE), value = TRUE)
script_dir <- if (length(script_arg)) dirname(normalizePath(sub("^--file=", "", script_arg[[1]]))) else getwd()
root <- dirname(script_dir)
source(file.path(root, "model", "R", "routeb_model.R"))

assert_close <- function(a,b,tol=1e-10,msg="") {
  if (!is.finite(a) || !is.finite(b) || abs(a-b)>tol) stop(sprintf("%s | %.17g vs %.17g",msg,a,b))
}

for (rho in seq(1e-5,0.999,length.out=900)) {
  xl <- scheduled_x_lambert(rho)
  xr <- scheduled_x_root(rho)
  assert_close(xl,xr,2e-9,"Lambert vs root")
  assert_close(inspection_balance_exp(xl),rho,2e-11,"FOC")
  assert_close(rho/xl+stale_fraction_exp(xl),scheduled_min_variable(rho),2e-11,"minimum identity")
  if (!(xl > sqrt(2*rho))) stop("sqrt approximation must be below exact x*")
}

xs <- vapply(seq(0.001,0.999,length.out=400), scheduled_x_star, numeric(1))
if (!all(diff(xs)>0)) stop("x*(rho) monotonicity failed")

for (rho in seq(0.01,0.95,length.out=120)) {
  phi <- 0.2*scheduled_min_variable(rho)
  d <- cadence_break_even_root(rho,phi=phi)
  assert_close(stale_fraction_exp(d),scheduled_min_variable(rho)-phi,2e-10,"cadence frontier")
}

for (shape in c(0.6,0.8,1,1.5,2,3)) {
  cap <- gamma(1+1/shape)
  for (frac in c(0.01,0.1,0.4,0.8,0.98)) {
    rho <- frac*cap; x <- weibull_x_star(rho,shape)
    assert_close(weibull_characteristic(x,shape),rho,4e-10,"Weibull FOC")
    assert_close(rho/x+weibull_stale_fraction(x,shape),weibull_min_variable(rho,shape),4e-10,"Weibull min identity")
  }
}
cat("All living-review maintenance R tests passed.\n")
