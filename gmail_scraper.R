library(gmailr)
library(dplyr)
library(XML)
library(stringr)

gmail_auth(secret_file = "Rugby-app.json", scope = 'full')

search_term = "label:ealing-rugby selection subject:Ealing Men's Rugby from:Ealing Men's Rugby"

getBody = function(id){
  body(message(id, format = 'full'))
}

# Retrieve message id's using the search query
ids = id(messages(search = search_term), what = "thread_id")
body_list = unique(lapply(ids, getBody))

body <- c(unlist(body_list[which(sapply(body_list, is.character))]),
          unlist(body_list[which(!sapply(body_list, is.character))]))

body1 <- unlist(body_list[which(sapply(body_list, is.character))])
body2 <- unlist(body_list[which(!sapply(body_list, is.character))])

get_team_tables <- function(body){
  team_tables <- readHTMLTable(body) %>%
    bind_rows(.id = "id") %>%
    filter(id == "team-table") %>%
    select(team = `Position/Team`, name = Name) %>%
    mutate(team = str_extract(team, "^[a-z0-9]+"))

  return(team_tables)
}

team_list1 <- get_team_tables(body1[1]) %>% mutate(body_id = 1)
for(i in 2:length(body1)){
  team_list <- bind_rows(team_list, get_team_tables(body1[i]) %>% mutate(body_id = i))
}

