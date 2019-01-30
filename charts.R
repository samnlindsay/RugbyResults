theme = hc_theme_google()
cols <- c("green", "orange", "grey", "black")

# GAMES BY SEASON
hc_games_by_season <- function(df){
  games_by_team <- df %>% count(Team, Season) %>%
    rename(Games = n)

  hchart(games_by_team, "column", hcaes(x = Season, y = Games, group = Team)) %>%
    #hc_title(text = "Games per season") %>%
    #hc_subtitle(text = "subtitle") %>%
    hc_colors(cols) %>%
    hc_add_theme(theme) %>%
    hc_legend(align = "left", verticalAlign = "top",
              layout = "vertical", floating = T, x = 70, y = 15) %>%
    hc_tooltip(shared = T, followPointer = T) %>%
    hc_yAxis(tickInterval = 5) %>%
    hc_plotOptions(column = list(dataLabels = list(enabled = T)))
}
#hc_games_by_season(df)

hc_tot_games_by_season <- function(df){
  games_by_team <- df %>% count(Start, Season) %>%
    rename(Games = n) %>%
    mutate(Start = ifelse(Start, "Start", "Bench"))

  hchart(games_by_team, "column", hcaes(x = Season, y = Games, group = Start)) %>%
    hc_colors(cols) %>%
    hc_add_theme(theme) %>%
    hc_yAxis(tickInterval = 5) %>%
    hc_plotOptions(column = list(
      dataLabels = list(enabled = T),
      stacking = "normal"
    )) %>%
    hc_legend(align = "left", verticalAlign = "top",
              layout = "vertical", floating = T, x = 60, y = 5)
}
#hc_tot_games_by_season(df)

# GAMES BY POSITION
hc_games_by_position <- function(df){
  games_by_position <- df %>%
    separate_rows(Position, sep = "/") %>%
    count(Team, Position) %>% rename(Games = n)

  hchart(games_by_position, "column", hcaes(x = Position, y = Games, group = Team)) %>%
    hc_add_theme(theme) %>%
    hc_colors(cols)  %>%
    hc_legend(align = "right", verticalAlign = "top",
              layout = "vertical", floating = T, x = -40, y = 5) %>%
    hc_plotOptions(column = list(dataLabels = list(enabled = T)))
}
#hc_games_by_position(df)

hc_tot_games_by_position <- function(df){
  games_by_position <- df %>%
    separate_rows(Position, sep = "/") %>%
    count(Position) %>% rename(Games = n) %>%
    mutate(Position = factor(Position, levels = c("Lock", "Flanker", "No. 8"))) %>%
    arrange(Position)

  hchart(games_by_position, "column", hcaes(x = Position, y = Games)) %>%
    hc_add_theme(theme) %>%
    hc_colors(cols)  %>%
    hc_legend(align = "right", verticalAlign = "top",
              layout = "vertical", floating = T, x = -40, y = 5) %>%
    hc_plotOptions(column = list(dataLabels = list(enabled = T)))
}
#hc_tot_games_by_position(df)


# GAMES BY TEAM
hc_tot_games_by_team <- function(df){
  games_by_team <- df %>% count(Team, Start) %>%
    rename(Games = n) %>%
    mutate(Start = ifelse(Start, "Start", "Bench"))
  cols <- c("green", "orange", "grey", "black")

  hchart(games_by_team, "column", hcaes(x = Team, y = Games, group = Start)) %>%
    hc_colors(cols) %>%
    hc_add_theme(theme) %>%
    hc_legend(align = "left", verticalAlign = "top",
              layout = "vertical", floating = T, x = 70, y = 15) %>%
    hc_tooltip(shared = T, followPointer = T) %>%
    hc_yAxis(tickInterval = 5) %>%
    hc_plotOptions(
      #series = list(colorByPoint = T),
      column = list(
        dataLabels = list(enabled = T),
        stacking = "normal")) %>%
    hc_legend(align = "left", verticalAlign = "top",
              layout = "vertical", floating = T, x = 60, y = 5)
}
#hc_tot_games_by_team(df)

# MINS BY TEAM
hc_tot_mins_by_team <- function(df){
  mins_by_team <- df %>%
    group_by(Team) %>%
    summarise(`Minutes` = round(sum(Time, na.rm = T), -1))
  cols <- c("green", "orange", "grey", "black")

  hchart(mins_by_team, "column", hcaes(x = Team, y = Minutes)) %>%
    hc_colors(cols) %>%
    hc_add_theme(theme) %>%
    hc_legend(align = "left", verticalAlign = "top",
              layout = "vertical", floating = T, x = 70, y = 15) %>%
    hc_tooltip(shared = T, followPointer = T) %>%
    hc_yAxis(tickInterval = 400) %>%
    hc_plotOptions(series = list(colorByPoint = T),
                   column = list(dataLabels = list(enabled = T)))
}
#hc_tot_mins_by_team(df)

# TRIES
hc_tries <- function(df){
  tries <- df %>%
    group_by(Team, Season) %>%
    summarise(Tries = sum(Try, na.rm = T))

  hchart(tries, "column", hcaes(x = Season, y = Tries, group = Team))  %>%
    hc_add_theme(theme) %>%
    hc_colors(cols) %>%
    hc_yAxis(tickInterval = 1) %>%
    hc_legend(align = "left", verticalAlign = "top",
              layout = "vertical", floating = T, x = 70, y = 15) %>%
    hc_plotOptions(column = list(stacking = "normal",
                                 dataLabels = list(enabled = T)))
}
#hc_tries(df)

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
    hc_legend(align = "right", layout = "vertical", verticalAlign = "top") %>%
    hc_tooltip(crosshairs = T,
               pointFormat = "<b>Season:</b> {point.Season} <br> {point.F} - {point.A} <br> {point.Opposition} ({point.Home/Away})") %>%
    hc_yAxis(tickInterval = 20) %>%
    hc_xAxis(tickInterval = 10, min = 0, max = 60)
}
#hc_score_map(df)


# CUMULATIVE GAME TIME
hc_cum_time <- function(df){
  cum_count <- df %>%
    group_by(Season) %>%
    mutate(days_since_Jul = Date - years(strtrim(Season, 4)) - as.Date("0000-07-01"),
           cum_games = row_number(),
           cum_mins = cumsum(Time),
           date = as.Date("2018-07-01") + days(days_since_Jul)) %>%
    select(Season, cum_games, cum_mins, date, Date)

  hchart(cum_count, "line", hcaes(x = date, y = cum_mins, group = Season)) %>%
    hc_legend(layout = "vertical", align = "left", verticalAlign = "top",
              floating = T, x = 100) %>%
    hc_yAxis(title = list(text = "Minutes Played")) %>%
    hc_xAxis(title = list(text = "Date"),
             type = "datetime",
             dateTimeLabelFormats = list(day = "%e %b", month = "%B")) %>%
    hc_tooltip(crosshairs = T, dateTimeLabelFormats = list(day = "%e %b")) %>%
    hc_add_theme(theme)
}
#hc_cum_time(df)

# CUMULATIVE GAMES
hc_cum_games <- function(df){
  cum_count <- df %>%
    group_by(Season) %>%
    mutate(days_since_Jul = Date - years(strtrim(Season, 4)) - as.Date("0000-07-01"),
           cum_games = row_number(),
           cum_mins = cumsum(Time),
           date = as.Date("2018-07-01") + days(days_since_Jul)) %>%
    select(Season, cum_games, cum_mins, date, Date)

  hchart(cum_count, "line", hcaes(x = date, y = cum_games, group = Season)) %>%
    hc_legend(layout = "vertical", align = "left", verticalAlign = "top",
              floating = T, x = 100) %>%
    hc_yAxis(title = list(text = "Games Played")) %>%
    hc_xAxis(title = list(text = "Date"),
             type = "datetime",
             dateTimeLabelFormats = list(day = "%e %b", month = "%B")) %>%
    hc_tooltip(dateTimeLabelFormats = list(day = "%e %b")) %>%
    hc_add_theme(theme)
}
#hc_cum_games(df)

###############################################################################

posneg_gradient <- function(x){
  x = eval(parse(text = x))
  pos <- which(x >= 0)
  neg <- which(x < 0)
  max <- max(abs(x)) # max value for normalising
  color = matrix(255, nrow = 4, ncol = length(x), dimnames = list(c("red", "green", "blue", "alpha")))
  color[1:3, pos] = gradient(c(0, max, x[pos]), "white", "green3")[, c(-1, -2)] # 0 = white, max = green
  color[1:3, neg] = gradient(c(0, -max, x[neg]), "red", "white")[, c(-1, -2)] # 0 = white, -max = red
  color[4, ] = 170
  return(color)
}

posneg_color_tile <- formatter("span",
                               style = function(x) style(display = "block",
                                                         padding = "0px",
                                                         `border-radius` = "2px",
                                                         `background-color` = csscolor(posneg_gradient(x), format = "rgba")))

dt_average_score_season <- function(df){
  average_score_by_season <- df %>%
    group_by(Season, `Home/Away`) %>%
    summarise(`F` = round(mean(`F`)),
              `A` = round(mean(`A`)),
              Games = n())

  average_score <- df %>%
    group_by(`Home/Away`) %>%
    summarise(`F` = round(mean(`F`)),
              `A` = round(mean(`A`)),
              Games = n()) %>%
    mutate(Season = "Overall")

  average_score2 <- bind_rows(average_score_by_season, average_score) %>%
    mutate(Score = paste0(`F`, " - ", `A`),
           ` ` = ifelse(`Home/Away` == "H", "Home", "Away")) %>%
    select(Season, ` `, Score) %>%
    spread(Season, Score) %>%
    arrange(desc(` `)) %>%
    mutate_all(funs(ifelse(is.na(.), "-",.)))

  dt <- formattable(average_score2,
                    align = c("r", "c", "c", "c", "c", "c"),
                    list(
                      ` ` = formatter("span", style = ~ style(font.weight = "bold"))
                    ))
  return(dt)
}
#dt_average_score_season(df)


dt_average_score_team <- function(df){
  average_score_by_team <- df %>%
    group_by(Team, `Home/Away`) %>%
    summarise(`F` = round(mean(`F`)),
              `A` = round(mean(`A`)),
              Games = n())

  average_score <- df %>%
    group_by(`Home/Away`) %>%
    summarise(`F` = round(mean(`F`)),
              `A` = round(mean(`A`)),
              Games = n()) %>%
    mutate(Team = "Overall")

  average_score2 <- bind_rows(average_score_by_team, average_score) %>%
    mutate(Score = paste0(`F`, " - ", `A`),
           ` ` = ifelse(`Home/Away` == "H", "Home", "Away")) %>%
    select(Team, ` `, Score) %>%
    spread(Team, Score) %>%
    arrange(desc(` `)) %>%
    mutate_all(funs(ifelse(is.na(.), "-",.)))

  dt <- formattable(average_score2,
                    align = c("r", "c", "c", "c", "c", "c"),
                    list(
                      ` ` = formatter("span", style = ~ style(font.weight = "bold")
                      ))
  )
  return(dt)
}
#dt_average_score_team(df)

dt_win_rate <- function(df){
  win_rate <- df %>%
    group_by(Team, Season) %>%
    summarise(Games = n(),
              Wins = sum(Result == "W")) %>%
    mutate(win_rate = scales::percent(Wins/Games))

  win_rate_by_team <- win_rate %>%
    group_by(Team) %>%
    summarise(Games = sum(Games),
              Wins = sum(Wins)) %>%
    mutate(win_rate = scales::percent(Wins/Games),
           Season = "Overall")

  win_rate2 <- bind_rows(win_rate, win_rate_by_team) %>%
    select(Team, Season, win_rate) %>%
    rename(` ` = Team) %>%
    spread(Season, win_rate) %>%
    mutate_all(funs(ifelse(is.na(.), "-",.)))

  dt <- formattable(win_rate2,
                    align = c("r", "c", "c", "c", "c", "c"),
                    list(
                      ` ` = formatter("span", style = ~ style(font.weight = "bold")
                      )))

  return(dt)
}
#dt_win_rate(df)


###############################################################

#data(citytemp)

#hc <- highchart() %>%
#  hc_xAxis(categories = citytemp$month) %>%
#  hc_add_series(name = "Tokyo", data = citytemp$tokyo) %>%
#  hc_add_series(name = "London", data = citytemp$london) %>%
#  hc_add_series(name = "Other city",
#                data = (citytemp$tokyo + citytemp$london)/2)

#hc
