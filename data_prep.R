library(dplyr)
library(tidyr)
library(stringr)
library(lubridate)
library(readr)

raw <- read_csv("Rugby_original.csv")

data <- raw %>%
  mutate(Date = as.Date(Date, format = "%d/%m/%y"),
         Team = as.factor(Team),
         Venue = ifelse(str_detect(`Home/Away`, "@"),
                        str_extract(`Home/Away`, "(?<=@)\\w+(?=\\))"),
                        ifelse(`Home/Away` == "A", "Away", "Ealing")),
         `Home/Away` = as.factor(substr(`Home/Away`,1,1)),
         Season = ifelse(month(Date) < 6,
                         paste0(year(Date) - 1, "/", year(Date)),
                         paste0(year(Date), "/", year(Date) + 1)),
         Result = as.factor(Result),
         MOTM = str_detect(Time, "M"),
         Start = !str_detect(Time, "R"),
         YC = str_detect(Time, "Y"),
         Try = str_count(Time, "T"),
         Time = as.integer(str_extract(Time, "^\\d+")),
         Stage = NA) %>%
  separate(Score, c("Home", "sep", "Away"), sep = "\\s") %>%
  separate(Position, c("Position", "Alternate Position"), sep = "/", fill = "right") %>%
  mutate(`F` = as.integer(ifelse(str_detect(`Home/Away`, "^H"), Home, Away)),
         `A` = as.integer(ifelse(str_detect(`Home/Away`, "^A"), Home, Away)),
         Notes = ifelse(str_detect(sep, "^\\w"), sep, NA_character_)) %>%
  select(Season, Date, Team, Competition, Stage, Opposition, `Home/Away`, Venue,
         Result, `F`, `A`,
         Position, Time, Start, MOTM, YC, Try, Notes)

data$Stage[str_detect(data$Competition, "SF$")] = "Semi Final"
data$Stage[str_detect(data$Competition, "QF$")] = "Quarter Final"
data$Stage[str_detect(data$Competition, "Play-Off Final$")] = "Play-Off Final"
data$Stage[str_detect(data$Competition, "Final$")] = "Final"

data$Competition <- str_replace(data$Competition, "\\sSF|\\sQF|\\sPlay-Off Final$|\\sFinal", "")

data$Stage <- as.factor(data$Stage)

write_csv(data, "Rugby_clean.csv")
