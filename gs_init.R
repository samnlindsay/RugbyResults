library(googlesheets)

sheets <- gs_ls()

rugby <- gs_title("Rugby_data")

data <- gs_read(rugby, ws = 1)
team_lists <- gs_read(rugby, ws = 2)
