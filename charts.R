# GAMES BY TEAM
games_by_team <- df %>% count(Team, Season) %>%
  rename(Games = n)
cols <- c("green", "orange", "grey", "black")

hchart(games_by_team, "column", hcaes(x = Season, y = Games, group = Team)) %>%
  hc_colors(cols) %>%
  hc_add_theme(hc_theme_google()) %>%
  hc_legend(align = "left", verticalAlign = "top",
            layout = "vertical", floating = T, x = 70, y = 15) %>%
  hc_tooltip(shared = T, followPointer = T)

# TRIES
tries <- df %>%
  group_by(Team, Season) %>%
  summarise(Tries = sum(Try, na.rm = T))

hchart(tries, "column", hcaes(x = Season, y = Tries, color = Team))  %>%
  hc_add_theme(hc_theme_google()) %>%
  hc_colors(cols)

# SCORE MAP
hchart(df, "scatter", hcaes(x = `F`, y = `F` - `A`, group = Team)) %>%
  hc_colors(cols) %>%
  hc_add_theme(hc_theme_google()) %>%
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


# Cumulative Games/Minutes
cum_mins <- df %>%
  group_by(Season) %>%
  mutate(days_since_Jul = Date - years(strtrim(Season, 4)) - as.Date("0000-07-01"),
         cum_mins = cumsum(Time),
         cum_games = row_number(),
         date = as.Date("2018-07-01") + days(days_since_Jul)) %>%
  select(Season, days_since_Jul, cum_mins, cum_games, date, Date)

hchart(cum_mins, "line", hcaes(x = date, y = cum_games, group = Season)) %>%
  hc_legend(layout = "vertical", align = "right", verticalAlign = "middle") %>%
  hc_yAxis(title = list(text = "Games Played")) %>%
  hc_xAxis(title = list(text = "Date"),
           type = "datetime",
           dateTimeLabelFormats = list(day = "%e %b", month = "%B")) %>%
  hc_tooltip(dateTimeLabelFormats = list(day = "%e %b"))

