library(gmailr)
library(dplyr)
library(readr)
library(XML)
library(stringr)
library(glue)

# Configure ---------------------------------------------------------------
gm_auth_configure(path = "Rugby-app.json")
gm_auth(email = "sam.n.lindsay@gmail.com", cache = ".secret")


#min_date = format(as.Date("2019-01-01"), "%Y/%m/%d")
scrape_gmail <- function(min_date = "2015-10-01"){
  # Get raw email data ------------------------------------------------------
  search_term = glue("label:ealing-rugby
                   subject:details
                   subject:-dinner
                   subject:-tour
                   subject:-kinsale
                   to:sam.n.lindsay@gmail.com
                   -mensmanagers@googlegroups.com
                   after:{min_date}")

  messages = gm_messages(search = search_term, num_results = 10000)
  ids = gm_id(messages)
  body_list = sapply(ids, function(x) gm_body(gm_message(x)))
  date_list = sapply(ids, function(x) gm_date(gm_message(x)))

  if(length(body_list) > 0){
    # Extract new format tables (post-2018) -----------------------------------

    get_team_tables <- function(body){
      team_tables <- readHTMLTable(body, stringsAsFactors = F) %>%
        bind_rows(.id = "id") %>%
        filter(str_detect(id, "team-table") | id == "NULL") %>%
        select(-starts_with("V")) %>%
        as_tibble()
      return(team_tables)
    }

    table_new <- purrr::map(body_list, get_team_tables)

    for(i in 1:length(table_new)){
      if(length(table_new[[i]]) > 0) table_new[[i]]$date = as.character(date_list[i])
    }

    table_new <- table_new %>%
      bind_rows() %>%
      purrr::compact() %>%
      select(team = `Position/Team`, name = Name, date) %>%
      mutate(cap = str_detect(team, " (?<!v)cap"),
             pos = str_extract(team, "(?<=-)\\d+"),
             team = str_extract(team, "^\\w+")) %>%
      filter(!is.na(name))


    # Extract old format tables (MESSY!) --------------------------------------

    regex1 = "(?<=\\n)(1|2(nd)?|ex|ev(e)?)(-{1,2}|:)?(\\d{1,2})?((\\s|-)cap)?\\s*([a-zA-Z-]+('[a-zA-Z-])?[a-zA-Z-]*\\s){1,3}(?=\\s*(Mem|Aca|NON|Stud|Under|Social))"
    regex2 = "(?<=\\n)(\\d{1,2}\\.?\\s*)?([a-zA-Z-]+('[a-zA-Z-])?[a-zA-Z-]*\\s?){1,3}(?=\\(C\\)|\\r)"

    extract_names <- function(body, regex = regex1){
      names <- body %>%
        str_extract_all(regex) %>%
        unlist() %>%
        as.data.frame(stringsAsFactors = F)
      return(names)
    }

    table_old1 <- sapply(unlist(body_list), extract_names, regex1) %>%
      `names<-`(as.character(date_list)) %>%
      stack() %>%
      rename(text = values,
             date = ind)

    table_old2 <- sapply(unlist(body_list), extract_names, regex2) %>%
      `names<-`(as.character(date_list)) %>%
      stack() %>%
      rename(text = values,
             date = ind)

    table_old <- table_old2 %>%
      filter(!(date %in% table_old1$date)) %>%
      bind_rows(table_old1) %>%
      filter(!str_detect(text, "(Vallis)|(United)|(----)|direct|(Thank you)|(Ricky)|Team")) %>%
      mutate(date = as.character(date),
             cap = str_detect(text, "cap"),
             pos = str_extract(text, "(?<=-)\\d+|^\\d+(?<=\\s\\w)"),
             team = str_extract(text, "^(1(?!\\d)|2(?!\\d)|ex|ev(e)?)?(?!\\.)"),
             name = str_extract(text, "(\\s?[a-zA-Z-']*)*$") %>%
               str_replace_all("^\\s?(1|2|ex|ev(e)?)?\\s?(-{1,2}|:)?\\s?(cap)?\\s?", "") %>%
               str_replace_all("^(nd|cap)", "") %>%
               str_trim()) %>%
      select(team, name, date, cap, pos)



    # Join tables -------------------------------------------------------------
    team_lists <- bind_rows(table_new, table_old) %>%
      #filter(team != "",
      #       name != "") %>%
      mutate(name = str_to_title(name),
             date = as.POSIXct(date, format = "%a, %d %b %Y %T"),
             team = case_when(
               .$team == "ex" ~ "Exiles",
               .$team %in% c("ev", "eve") ~ "Evergreens",
               .$team %in% c("1", "a") ~ "1st",
               .$team == "2" ~ "2nd",
               TRUE ~ "unknown"
             ),
             pos = as.numeric(pos)) %>%
      group_by(team, date2 = as.Date(date)) %>%
      filter(date == max(date)) %>%
      ungroup() %>%
      mutate(date = date2) %>%
      select(team, name, date, cap, pos)


    # Fixes -------------------------------------------------------------------

    team_lists$team[team_lists$date == "2016-04-22"] <- "2nd"
    team_lists$team[team_lists$date == "2016-04-29"] <- "Exiles"
    team_lists$team[team_lists$date == "2016-08-24"] <- "2nd"
    team_lists$team[team_lists$date == "2017-08-17"] <- "1st"
    team_lists$team[team_lists$date == "2017-08-22"] <- "2nd"

    if(min_date <= "2019-01-10"){
      missing <- read_csv("2019-01-10.csv") %>%
        mutate(date = as.Date("2019-01-10"),
               cap = str_detect(team, "cap"),
               pos = as.numeric(str_extract(team, "(?<=-)\\d+|^\\d+(?<=\\s\\w)")),
               team = str_extract(team, "^(1(?!\\d)|2(?!\\d)|ex|ev(e)?)?"),
               name = str_replace_all(name, "\\t", "")) %>%
        mutate(team = case_when(
          .$team == "ex" ~ "Exiles",
          .$team %in% c("ev", "eve") ~ "Evergreens",
          .$team == "1" ~ "1st",
          .$team == "2" ~ "2nd"
        ))
      team_lists <- bind_rows(team_lists, missing)
    }

    # Name corrections
    team_lists$name = team_lists$name %>%
      str_replace("Abderrahmane", "Abdou") %>%
      str_replace("Eubank ", "Eubank-") %>%
      str_replace("Piri$", "Pirinoli") %>%
      str_replace("Alexander", "Alex") %>%
      str_replace("Alfred", "Alfie") %>%
      str_replace("Ingslamb", "Ings-Lamb") %>%
      str_replace("Ashley", "Ash") %>%
      str_replace("Brendan O.*", "Brendan O'Flaherty") %>%
      str_replace("Nolal ", "Nolan-") %>%
      str_replace("Cal+um Nolan.*", "Callum Nolan-Hutchinson") %>%
      str_replace("Calum", "Callum") %>%
      str_replace("^Cap\\s", "") %>%
      str_replace("Chris Fenn", "Christopher Fenn") %>%
      str_replace("Mansel$", "Mansell") %>%
      str_replace("Conelly", "Connelly") %>%
      str_replace("Daniel", "Dan") %>%
      str_replace("David M.*", "David McSweeney") %>%
      str_replace("Dav.+ Ste+ne", "David Steene") %>%
      str_replace("Devin", "Devon") %>%
      str_replace("Dwaid Chopz", "Dawid Czop") %>%
      str_replace("Eoghan O.*", "Eoghan O'Sullivan") %>%
      str_replace("Fillippe", "Filippe") %>%
      str_replace("Jacon", "Jacob") %>%
      str_replace("Jonahan", "Jonathan") %>%
      str_replace("Joseph Newnham", "Joe Newnham") %>%
      str_replace("^J.*Hoban$", "John-Paul Hoban") %>%
      str_replace("^Ka.*son$", "Kacie Addison") %>%
      str_replace("Kairo R.*$", "Kairo Rodrigo-Payne") %>%
      str_replace("Langford Rhys", "Rhys Langford") %>%
      str_replace("Liam Mcd.*", "Liam McDonagh") %>%
      str_replace("Liam Woodford", "Liam Woolford") %>%
      str_replace("Lovette$", "Lovette Burland") %>%
      str_replace("Luca Town.*", "Luca Townshend") %>%
      str_replace("Matt C Jones", "Matt Jones") %>%
      str_replace("Matthew", "Matt") %>%
      str_replace("Maz Z.*$", "Max Ziya-Zadeh") %>%
      str_replace("Mi.* Rug.*$", "Mike Rugeley") %>%
      str_replace("Mc Minn", "Mcminn") %>%
      str_replace("Moicea", "Moceica") %>%
      str_replace("^Michael", "Mike") %>%
      str_replace("Munema", "Munemo") %>%
      str_replace("Nial Wake", "Nyall Wake") %>%
      str_replace("Nyasha.*Munemo$", "Sean Munema") %>%
      str_replace("Patrick Nash", "Pat Nash") %>%
      str_replace("Oliver Mayo", "Olly Mayo") %>%
      str_replace("Oliver Morris", "Ollie Morris") %>%
      str_replace("Rao?ul F.*", "Raoul Fereira") %>%
      str_replace("Roderick", "Rod") %>%
      str_replace("Samms Rasaan", "Rasaan Samms") %>%
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

    return(team_lists)
  }

}

#all_team_lists <- scrape_gmail(min_date = "2015-10-01")

# Join to match data #-----------------------------------------------

#data <- read_csv("Rugby_clean.csv")

# match my dates with most recent selection date by team
add_match_dates <- function(data, team_lists){
  team_lists2 <- data %>%
    select(Team, Date) %>%
    full_join(team_lists, by = c("Team" = "team")) %>%
    mutate(diff = Date - date) %>%
    filter(diff >= 0, diff < 5) %>%
    unique() %>%
    group_by(Team, Date) %>%
    filter(date == max(date)) %>%
    ungroup() %>%
    select(Team, name, Date, cap, pos)
  #summarise(team_list = list(name))
  return(team_lists2)
}

#team_lists2 <- add_match_dates(data, all_team_lists)

# Add HTML team sheet to match data ---------------------------------
add_html_team <- function(data, team_lists){
  df <- left_join(data, team_lists, by = c("Date", "Team")) %>%
    group_by_at(vars(-c(pos, cap, name))) %>%
    unique() %>%
    arrange(pos) %>%
    mutate(html = glue("<b>{pos}</b> - {name}{ifelse(cap, ' (C)','')}", .na = "")) %>%
    summarise(name = glue_collapse(html, sep = "<br>")) %>%
    ungroup()
  return(df)
}

