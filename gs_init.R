library(googlesheets)

sheets <- gs_ls()

rugby <- gs_title("Rugby_data")
rugby$sheet_key     # 1keX2eGbyiBejpfMPMbL7aXYLy7IDJZDBXQqiKVQavz0


rugby <- gs_key("1keX2eGbyiBejpfMPMbL7aXYLy7IDJZDBXQqiKVQavz0")
data <- gs_read(rugby)
