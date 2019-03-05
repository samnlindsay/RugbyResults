library(gmailr)
library(dplyr)
library(XML)
library(stringr)

gmail_auth(secret_file = "Rugby-app.json", scope = 'full')

search_term = "label:ealing-rugby selection subject:Ealing Men's Rugby from:Ealing Men's Rugby to:sam.n.lindsay@gmail.com"

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

# Retrieve messages using the search query
ids = gmailr::id(messages(search = search_term), what = "thread_id")
body_list = lapply(ids, getBody)
from_list = unlist(lapply(ids, getFrom))
to_list = unlist(lapply(ids, getTo))
date_list = unlist(lapply(ids, getDate))
subject_list = unlist(lapply(ids, getSubject))

table <- cbind(from_list, to_list, date_list, subject_list, unlist(body_list)) %>%
  as.data.frame(stringsAsFactors = F) %>%
  filter(str_detect(to_list, "sam.n.lindsay@gmail.com"))

extract_names <- function(body){
  names <- body %>%
    str_extract_all("\\w+-\\d+\\s[\\w+ ?]+(?=\\w)") %>%
    unlist()
  return(names)
}

get_team_tables <- function(body){
  team_tables <- readHTMLTable(body, stringsAsFactors = F) %>%
    bind_rows(.id = "id") %>%
    filter(id == "team-table") %>%
    select(team = `Position/Team`, name = Name) %>%
    mutate(team = str_extract(team, "^\\w+"))

  return(team_tables)
}

new <- which(sapply(body_list, is.character))
old <- which(!sapply(body_list, is.character))

table_new <- table[new, ]
table_old <- table[old, ]

team_list_new <- get_team_tables(table_new$V5[1]) %>%
  mutate(date_list = table_new$date_list[1])
for(i in 2:length(table_new)){
  team_list_new <- team_list_new %>%
    bind_rows(get_team_tables(table_new$V5[i]) %>%
                mutate(date_list = table_new$date_list[i]))
}

team_list_old <- extract_names(table_old$V5[1]) %>%
  as.data.frame(stringsAsFactors = F) %>%
  mutate(date_list = table_old$date_list[1])
for(i in 2:length(table_old)){
  team_list_old <- team_list_old %>%
    bind_rows(extract_names(table_old$V5[i]) %>%
                as.data.frame(stringsAsFactors = F) %>%
                mutate(date_list = table_old$date_list[i]))
}