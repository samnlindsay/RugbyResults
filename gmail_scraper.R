library(gmailr)
library(dplyr)
library(XML)
library(stringr)

gmail_auth(secret_file = "Rugby-app.json", scope = 'full')

search_term = "label:ealing-rugby selection subject:Ealing Men's Rugby from:Ealing Men's Rugby"

getBody = function(id){
  body(message(id, format = 'full'))
}

getFrom = function(id){
  from(message(id, format = "full"))
}

getTo = function(id){
  to(message(id, format = "full"))
}

getDate = function(id){
  date(message(id, format = "full"))
}

getSubject = function(id){
  subject(message(id, format = "full"))
}

# Retrieve message id's using the search query
ids = id(messages(search = search_term), what = "thread_id")
body_list = lapply(ids, getBody)
from_list = unlist(lapply(ids, getFrom))
to_list = unlist(lapply(ids, getTo))
date_list = unlist(lapply(ids, getDate))
subject_list = unlist(lapply(ids, getSubject))

table <- cbind(from_list, to_list, date_list, subject_list, unlist(body_list)) %>%
  as.data.frame()





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
  team_list1 <- bind_rows(team_list1, get_team_tables(body1[i]) %>% mutate(body_id = i))
}

body2[1]
