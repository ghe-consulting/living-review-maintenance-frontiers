dir.create("environment", showWarnings = FALSE)
writeLines(capture.output(sessionInfo()), "environment/R_sessionInfo.txt")
