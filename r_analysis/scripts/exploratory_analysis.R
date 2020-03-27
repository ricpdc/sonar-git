library(carData)
library(car)
scatterplot(committers ~ code_smells, data = sonar_git)



View(sonar_git)
x<-sonar_git$commits
y<-sonar_git$duplicated_lines
plot(x, y, main = "Main title",
       +      xlab = "X axis title", ylab = "Y axis title",
       +      pch = 19, frame = FALSE)
abline(lm(y ~ x, data = mtcars), col = "blue")

plot(sonar_git)



library(dplyr)
filter1<-select(sonar_git, 5:12, bugs, classes, code_smells, cognitive_complexity, file_complexity, coverage, critical_violations, complexity, duplicated_blocks, duplicated_files, duplicated_lines, duplicated_lines_density, violations, line_coverage, major_violations, minor_violations, open_issues, uncovered_lines, tests)

View(filter1)
plot(filter1)