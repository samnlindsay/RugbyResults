theme = hc_theme_google()


# GAMES BY SEASON
hc_games_by_season <- function(df){
  games_by_team <- df %>% count(Team, Season) %>%
    rename(Games = n)
  cols <- c("green", "orange", "grey", "black")

  hchart(games_by_team, "column", hcaes(x = Season, y = Games, group = Team)) %>%
    hc_colors(cols) %>%
    hc_add_theme(theme) %>%
    hc_legend(align = "left", verticalAlign = "top",
              layout = "vertical", floating = T, x = 70, y = 15) %>%
    hc_tooltip(shared = T, followPointer = T) %>%
    hc_yAxis(tickInterval = 5)
}
hc_games_by_season(df)

# GAMES BY POSITION
hc_games_by_position <- function(df){
  games_by_position <- df %>%
    separate_rows(Position, sep = "/") %>%
    count(Team, Position) %>% rename(Games = n)

  hchart(games_by_position, "column", hcaes(x = Position, y = Games, group = Team)) %>%
    hc_add_theme(theme) %>%
    hc_colors(cols)
}
hc_games_by_position(df)


# GAMES BY TEAM
hc_games_by_team <- function(df){
  games_by_team <- df %>% count(Team) %>%
    rename(Games = n)
  cols <- c("green", "orange", "grey", "black")

  hchart(games_by_team, "column", hcaes(x = Team, y = Games)) %>%
    hc_colors(cols) %>%
    hc_add_theme(theme) %>%
    hc_legend(align = "left", verticalAlign = "top",
              layout = "vertical", floating = T, x = 70, y = 15) %>%
    hc_tooltip(shared = T, followPointer = T) %>%
    hc_yAxis(tickInterval = 5)
}
hc_games_by_team(df)

# TRIES
hc_tries <- function(df){
  tries <- df %>%
    group_by(Team, Season) %>%
    summarise(Tries = sum(Try, na.rm = T))

  hchart(tries, "column", hcaes(x = Season, y = Tries, color = Team))  %>%
    hc_add_theme(theme) %>%
    hc_colors(cols) %>%
    hc_yAxis(tickInterval = 1)
  }
hc_tries(df)

# SCORE MAP
hc_score_map <- function(df){
  hchart(df, "scatter", hcaes(x = `F`, y = `F` - `A`, group = Team)) %>%
    hc_colors(cols) %>%
    hc_add_theme(theme) %>%
    hc_xAxis(title = list(text = "Points For"),
             plotBands = list(
               list(from = 0, to = 100, color = "rgba(100,100,100,0)",
                    label = list(text = "Lose",
                                 verticalAlign = "bottom", y = -25,
                                 align = "right", x = -35,
                                 style = list(fontSize = "20pt"))))) %>%
    hc_yAxis(title = list(text = "Points Difference"),
             plotLines = list(
               list(color = "black", width = 2, value = 0)),
             plotBands = list(
               list(from = 0, to = 100, color = "rgba(100,100,100,0.1)",
                    label = list(text = "Win",
                                 verticalAlign = "top", y = 25,
                                 style = list(fontSize = "20pt"))))) %>%
    hc_legend(verticalAlign = "top") %>%
    hc_tooltip(pointFormat = "<b>Season:</b> {point.Season} <br> {point.F} - {point.A} <br> {point.Opposition} ({point.Home/Away})")
}
hc_score_map(df)


# CUMULATIVE GAME TIME
hc_cum_games <- function(df, value = c("games", "mins")){
  cum_count <- df %>%
    group_by(Season) %>%
    mutate(days_since_Jul = Date - years(strtrim(Season, 4)) - as.Date("0000-07-01"),
           cum_games = row_number(),
           cum_mins = cumsum(Time),
           date = as.Date("2018-07-01") + days(days_since_Jul)) %>%
    select(Season, cum_count = ifelse(value == "games", cum_games, cum_mins), date, Date)

  hchart(cum_count, "line", hcaes(x = date, y = cum_count, group = Season)) %>%
    hc_legend(layout = "vertical", align = "right", verticalAlign = "middle") %>%
    hc_yAxis(title = list(text = ifelse(value == "mins", "Minutes Played", "Games Played"))) %>%
    hc_xAxis(title = list(text = "Date"),
             type = "datetime",
             dateTimeLabelFormats = list(day = "%e %b", month = "%B")) %>%
    hc_tooltip(dateTimeLabelFormats = list(day = "%e %b")) %>%
    hc_add_theme(theme)
}
hc_cum_games(df, "games")


###############################################################

data(citytemp)

hc <- highchart() %>%
  hc_xAxis(categories = citytemp$month) %>%
  hc_add_series(name = "Tokyo", data = citytemp$tokyo) %>%
  hc_add_series(name = "London", data = citytemp$london) %>%
  hc_add_series(name = "Other city",
                data = (citytemp$tokyo + citytemp$london)/2)

hc
