args <- commandArgs(trailingOnly = TRUE)
outfile <- if (length(args) >= 1) args[[1]] else "r_grid.csv"
script_arg <- grep("^--file=", commandArgs(FALSE), value = TRUE)
script_dir <- if (length(script_arg)) dirname(normalizePath(sub("^--file=", "", script_arg[[1]]))) else getwd()
root <- dirname(script_dir)
source(file.path(root, "model", "R", "routeb_model.R"))

rho_grid <- unique(c(seq(0.0001, 0.99, length.out = 600), 0.001, 0.01, 0.1, 0.5, 0.9, 0.999))
out <- do.call(rbind, lapply(rho_grid, function(rho) {
  xl <- scheduled_x_star(rho)
  xr <- scheduled_x_root(rho)
  data.frame(rho=rho, x_star=xl, x_root=xr,
             min_variable=scheduled_min_variable(rho),
             foc_residual=inspection_balance_exp(xl)-rho)
}))
# Base R write.csv/write.table has no digits= argument. Set process-local
# display precision instead; model/grid definitions are otherwise unchanged.
options(digits = 17)
write.csv(out, outfile, row.names = FALSE)
