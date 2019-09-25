library(gmailr)
library(dplyr)
library(XML)
library(stringr)

gmail_auth(secret_file = "Rugby-app.json", scope = 'full')

#search_term = "label:ealing-rugby subject:Ealing Men's Rugby selection -availability from:Ealing Men's Rugby to:sam.n.lindsay@gmail.com"
search_term_1719 = "label:ealing-rugby subject:details subject:-dinner subject:-tour subject:-kinsale to:sam.n.lindsay@gmail.com -mensmanagers@googlegroups.com after:2017/07/01"
search_term_1517 = "label:ealing-rugby subject:details subject:-dinner subject:-tour subject:-kinsale to:sam.n.lindsay@gmail.com -mensmanagers@googlegroups.com before:2017/07/01"

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
  gmailr::date(message(id, format = "full"))
}

getSubject = function(id){
  subject(message(id, format = "full"))
}

# Retrieve messages using the search query
ids_old = gmailr::id(messages(search = search_term_1517), what = "message_id")
ids_new = gmailr::id(messages(search = search_term_1719), what = "message_id")
ids = c(ids_old, ids_new)
body_list = lapply(ids, getBody)
from_list = unlist(lapply(ids, getFrom))
to_list = unlist(lapply(ids, getTo))
date_list = unlist(lapply(ids, getDate))
subject_list = unlist(lapply(ids, getSubject))

table <- cbind(from_list, to_list, date_list, subject_list, unlist(body_list)) %>%
  as.data.frame(stringsAsFactors = F) %>%
  rename(text = V5)

new <- which(sapply(body_list, is.character))
old <- which(!sapply(body_list, is.character))

table_new <- table[new, ]
table_old <- table[old, ]

# New method #---------------------------------

get_team_tables <- function(body){
  team_tables <- readHTMLTable(body, stringsAsFactors = F) %>%
    bind_rows(.id = "id") %>%
    filter(str_detect(id, "team-table") | id == "NULL") %>%
    select(team = `Position/Team`, name = Name) %>%
    mutate(cap = str_detect(team, "cap"),
           pos = str_extract(team, "(?<=-)\\d+"),
           team = str_extract(team, "^\\w+"))

  return(team_tables)
}

team_list_new <- get_team_tables(table_new$text[1]) %>%
  mutate(date_list = table_new$date_list[1])
for(i in 2:length(table_new$text)){
  team_list_new <- team_list_new %>%
    bind_rows(get_team_tables(table_new$text[i]) %>%
                mutate(date_list = table_new$date_list[i])) %>%
    filter(!is.na(name))
}
team_list_new <- left_join(table_new, team_list_new) %>%
  select(-text)

# Old method #-------------------------------------
extract_names <- function(body){
  names <- body %>%
    str_extract_all("(?<=\\n)(1|2(nd)?|ex|ev(e)?)(-{1,2}|:)?(\\d{1,2})?((\\s|-)cap)?\\s*([a-zA-Z-]+('[a-zA-Z-])?[a-zA-Z-]*\\s){1,3}(?=\\s*(Mem|Aca|NON|Stud|Under|Social))") %>%
    unlist()
  return(names)
}

team_list_old <- extract_names(table_old$text[1]) %>%
  as.data.frame(stringsAsFactors = F) %>%
  mutate(date_list = table_old$date_list[1])
for(i in 2:length(table_old$text)){
  team_list_old <- team_list_old %>%
    bind_rows(extract_names(table_old$text[i]) %>%
                as.data.frame(stringsAsFactors = F) %>%
                mutate(date_list = table_old$date_list[i]))
}


table_old2 <- table_old %>%
  filter(!(date_list %in% team_list_old$date_list))

extract_names2 <- function(body){
  names <- body %>%
    str_extract_all("(?<=\\n)(\\d{1,2}\\.?\\s*)?([a-zA-Z-]+('[a-zA-Z-])?[a-zA-Z-]*\\s?){1,3}(?=\\(C\\)|\\r)") %>%
    unlist()
  return(names)
}

team_list_old2 <- extract_names2(table_old2$text[1]) %>%
  as.data.frame(stringsAsFactors = F) %>%
  mutate(date_list = table_old2$date_list[1])
for(i in 2:length(table_old2$text)){
  team_list_old2 <- team_list_old2 %>%
    bind_rows(extract_names2(table_old2$text[i]) %>%
                as.data.frame(stringsAsFactors = F) %>%
                mutate(date_list = table_old2$date_list[i]))
}

team_list_old <- bind_rows(team_list_old, team_list_old2)
colnames(team_list_old)[1] <- "text"

team_list_old2 <- team_list_old %>%
  filter(!str_detect(text, "(Vallis)|(United)|(----)|direct|(Thank you)|(Ricky)|Team")) %>%
  mutate(cap = str_detect(text, "cap"),
         pos = str_extract(text, "(?<=-)\\d+|^\\d+(?<=\\s\\w)"),
         team = str_extract(text, "^(1(?!\\d)|2(?!\\d)|ex|ev(e)?)?"),
         name = str_extract(text, "(\\s?[a-zA-Z-']*)*$") %>%
           str_replace_all("^\\s?(1|2|ex|ev(e)?)?\\s?(-{1,2}|:)?\\s?(cap)?\\s?", "") %>%
           str_replace_all("^(nd|cap)", "") %>%
           str_trim()) %>%
  select(-text) %>%
  right_join(table_old) %>%
  select(-text)

# Fixes
team_list_old2$team[team_list_old2$date_list == "Thu, 17 Aug 2017 12:52:00 +0000"] <- "1"
team_list_old2$team[team_list_old2$date_list == "Tue, 22 Aug 2017 08:58:53 +0000"] <- "2"
team_list_old2$team[team_list_old2$date_list == "Wed, 24 Aug 2016 10:12:18 +0000"] <- "2"

# Combine team lists #--------------------------------------------

team_lists <- bind_rows(team_list_new, team_list_old2) %>%
  filter(team != "") %>%
  mutate(name = str_to_title(name),
         date = as.Date(date_list, format = "%a, %d %b %Y %T +0000"),
         team = case_when(
           .$team == "ex" ~ "Exiles",
           .$team %in% c("ev", "eve") ~ "Evergreens",
           .$team == "1" ~ "1st",
           .$team == "2" ~ "2nd"
         )) %>%
  select(-ends_with("list"))

# Fixes
team_lists$team[team_lists$date == "2016-04-22"] <- "2nd"
team_lists$team[team_lists$date == "2016-04-29"] <- "Exiles"

missing <- read_csv("2019-01-10.csv") %>%
  mutate(date = as.Date("2019-01-10"),
         cap = str_detect(team, "cap"),
         pos = str_extract(team, "(?<=-)\\d+|^\\d+(?<=\\s\\w)"),
         team = str_extract(team, "^(1(?!\\d)|2(?!\\d)|ex|ev(e)?)?"),
         name = str_replace_all(name, "\\t", "")) %>%
  mutate(team = case_when(
    .$team == "ex" ~ "Exiles",
    .$team %in% c("ev", "eve") ~ "Evergreens",
    .$team == "1" ~ "1st",
    .$team == "2" ~ "2nd"
  ))
team_lists <- bind_rows(team_lists, missing)

# Name corrections
team_lists$name = team_lists$name %>%
  str_replace("Abderrahmane", "Abdou") %>%
  str_replace("Piri$", "Pirinoli") %>%
  str_replace("Alexander", "Alex") %>%
  str_replace("Alfred", "Alfie") %>%
  str_replace("Ingslamb", "Ings-Lamb") %>%
  str_replace("Ashley", "Ash") %>%
  str_replace("Brendan O.*", "Brendan O'Flaherty") %>%
  str_replace("Cal+um Nolan.*", "Callum Nolan-Hutchinson") %>%
  str_replace("Calum", "Callum") %>%
  str_replace("^Cap\\s", "") %>%
  str_replace("Mansel$", "Mansell") %>%
  str_replace("Conelly", "Connelly") %>%
  str_replace("Daniel", "Dan") %>%
  str_replace("David M.*", "David McSweeney") %>%
  str_replace("Dav Ste+ne", "David Steene") %>%
  str_replace("Devin", "Devon") %>%
  str_replace("Dwaid Chopz", "Dawid Czop") %>%
  str_replace("Eoghan O.*", "Eoghan O'Sullivan") %>%
  str_replace("Fillippe", "Filippe") %>%
  str_replace("Jacon", "Jacob") %>%
  str_replace("^J.*Hoban$", "John-Paul Hoban") %>%
  str_replace("^Ka.*son$", "Kacie Addison") %>%
  str_replace("Langford Rhys", "Rhys Langford") %>%
  str_replace("Liam Mcd.*", "Liam McDonagh") %>%
  str_replace("Liam Woodford", "Liam Woolford") %>%
  str_replace("Lovette$", "Lovette Burland") %>%
  str_replace("Luca Town.*", "Luca Townshend") %>%
  str_replace("Matt C Jones", "Matt Jones") %>%
  str_replace("Matthew", "Matt") %>%
  str_replace("Mc Minn", "Mcminn") %>%
  str_replace("^Michael", "Mike") %>%
  str_replace("Nial Wake", "Nyall Wake") %>%
  str_replace("Nyasha.*Munemo$", "Sean Munema") %>%
  str_replace("Patrick Nash", "Pat Nash") %>%
  str_replace("Oliver Mayo", "Olly Mayo") %>%
  str_replace("Oliver Morris", "Ollie Morris") %>%
  str_replace("Rao?ul F.*", "Raoul Fereira") %>%
  str_replace("Roderick", "Rod") %>%
  str_replace("Sean Lion$", "Sean Munemo") %>%
  str_replace("Sean Lion Munemo", "Sean Munemo") %>%
  str_replace("Atick$", "Atik") %>%
  str_replace("Steven Dewsnip", "Stephen Dewsnip") %>%
  str_replace("Steven Richards", "Steve Richards") %>%
  str_replace(" Social$", "") %>%
  str_replace("Teejay", "Tee-Jay") %>%
  str_replace("Thomas Szysco", "Tom Szyszko") %>%
  str_replace("Thomas Szysco", "Tom Szyszko") %>%
  str_replace("Thomas Szyszco", "Tom Szyszko") %>%
  str_replace("Timothy", "Tim") %>%
  str_replace("Trevis", "Travis") %>%
  str_replace("Mc Gee", "Mcgee") %>%
  str_replace("Manuel Garcia ", "") %>%
  str_replace("Zeyala", "Zelaya") %>%
  str_replace("William Day", "Will Day")


# Join to match data #-----------------------------------------------
match_dates <- data %>%
  select(Team, Date)

selection_dates <- team_lists %>%
  #filter(name == "Sam Lindsay") %>%
  select(team, date)

# match my dates with most recent selection date by team
match_dates2 <- match_dates %>%
  left_join(selection_dates, by = c("Team" = "team")) %>%
  mutate(diff = Date - date) %>%
  filter(diff >= 0, diff < 7) %>%
  #select(-diff) %>%
  unique()


get_team_sheet <- function(my_team, match_date){
  if(match_date %in% match_dates2$Date){
    selection_date <- match_dates2 %>%
      filter(Team == my_team, Date == match_date) %>%
      .$date

    team_sheet <- team_lists %>%
      filter(date == selection_date, team == my_team) %>%
      unique() %>%
      select(name, pos, cap, team) %>%
      mutate(Date = match_date) %>%
      as.list()
  } else return()

    return(team_sheet)
}

add_team_sheets <- function(my_data){
  team_sheets <- get_team_sheet(my_data$Team[1], my_data$Date[1]) %>%
    as.data.frame(stringsAsFactors = F)
  for(i in 2:length(my_data$Team)){
    team_sheets <- rbind(team_sheets,
                         get_team_sheet(my_data$Team[i], my_data$Date[i]) %>%
                           as.data.frame(stringsAsFactors = F))
  }
  return(team_sheets)
}
