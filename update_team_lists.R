library(gmailr)
library(dplyr)
library(XML)
library(stringr)

gmail_auth(secret_file = "Rugby-app.json", scope = 'full')

latest_team_lists <- function(team_lists){
  max_date <- (max(as.Date(team_lists$date), na.rm = T) + days(1)) %>%
    format("%Y/%m/%d")

  search_term <- paste0("label:ealing-rugby subject:details subject:-dinner subject:-tour subject:-kinsale to:sam.n.lindsay@gmail.com -mensmanagers@googlegroups.com after:", max_date)

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
  ids = gmailr::id(messages(search = search_term), what = "message_id")

  if(length(ids) == 0){ return() }

  body_list = lapply(ids, getBody)
  from_list = unlist(lapply(ids, getFrom))
  to_list = unlist(lapply(ids, getTo))
  date_list = unlist(lapply(ids, getDate))
  subject_list = unlist(lapply(ids, getSubject))

  table <- cbind(from_list, to_list, date_list, subject_list, unlist(body_list)) %>%
    as.data.frame(stringsAsFactors = F) %>%
    rename(text = V5)

  get_team_tables <- function(body){
    team_tables <- readHTMLTable(body, stringsAsFactors = F) %>%
      bind_rows(.id = "id") %>%
      filter(str_detect(id, "team-table") | id == "NULL") %>%
      select(team = `Position/Team`, name = Name) %>%
      mutate(cap = str_detect(team, "cap"),
             pos = as.numeric(str_extract(team, "(?<=-)\\d+")),
             team = str_extract(team, "^\\w+"))

    return(team_tables)
  }

  team_list <- get_team_tables(table$text[1]) %>%
    mutate(date_list = table$date_list[1])
  if(length(table$text) > 1){
    for(i in 2:length(table$text)){
      team_list <- team_list %>%
        bind_rows(get_team_tables(table$text[i]) %>%
                    mutate(date_list = table$date_list[i])) %>%
        filter(!is.na(name))
  }
  }

  # Name corrections
  team_list$name = team_list$name %>%
    str_to_title() %>%
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
    str_replace("Nyasha.*Munemo$", "Sean Munemo") %>%
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

  team_list <- team_list %>%
    rename(date = date_list) %>%
    mutate(date = as.Date(date, format = "%a, %d %b %Y %T +0000")) %>%
    mutate(team = case_when(
      .$team == "ex" ~ "Exiles",
      .$team %in% c("ev", "eve") ~ "Evergreens",
      .$team == "1" ~ "1st",
      .$team == "2" ~ "2nd"
    ))

  return(team_list)
}

add_team_sheets <- function(my_data, team_lists){
  match_dates <- my_data %>%
    select(Team, Date)

  selection_dates <- team_lists %>%
    #filter(name == "Sam Lindsay") %>%
    select(team, date)

  # match my dates with most recent selection date by team
  match_dates2 <- match_dates %>%
    left_join(selection_dates, by = c("Team" = "team")) %>%
    mutate(diff = as.Date(Date) - date) %>%
    filter(diff >= 0, diff < 7) %>%
    #select(-diff) %>%
    unique()

  get_team_sheet <- function(team_lists, my_team, match_date){

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

  team_sheets <- get_team_sheet(team_lists, my_data$Team[1], my_data$Date[1]) %>%
    as.data.frame(stringsAsFactors = F)
  for(i in 2:length(my_data$Team)){
    team_sheets <- rbind(team_sheets,
                         get_team_sheet(team_lists, my_data$Team[i], my_data$Date[i]) %>%
                           as.data.frame(stringsAsFactors = F))
  }
  team_sheets <- team_sheets %>%
    group_by(team, Date) %>%
    mutate(names = paste0("<b>", pos, "</b> - <em>", name, "</em>", collapse = "<br>"))

  return(team_sheets)
}

add_html_team <- function(data, team_lists){
  data %>%
    left_join(add_team_sheets(data, team_lists), by = c("Date", "Team" = "team")) %>%
    select(-c(pos, name, cap)) %>%
    unique()
}



