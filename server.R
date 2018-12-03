library(shiny)
library(shinydashboard)
library(DT)
library(dplyr)
library(tidyr)
library(readr)
library(lubridate)
library(data.table)
library(shinyWidgets)
library(shinyjs)
library(highcharter)
library(formattable)
source("charts.R")

for_display <- function(df){
  df %>%
    mutate(Date = format(Date, "%d %b %Y"),
           Start = ifelse(Start, "<i class='fa fa-check' style='color:green' align='center'></i>", ""),
           MOTM = ifelse(MOTM, "<i class='fa fa-trophy' style='color:green' align='center'></i>", ""),
           YC = ifelse(YC, "<i class='fa fa-square' style='color:#ffcc00' align='center''></i>", ""),
           Try = ifelse(Try > 0, strrep("<i class='fa fa-star' style='color:green' align='center'></i>", Try), "")) %>%
    select(-Season, -`Home/Away`)
}

df <- read_csv("Rugby_clean.csv", col_types = "cDccccccciicilllicc") %>%
  mutate_at(c("Team", "Stage", "Home/Away", "Result"), as.factor)


function(input, output, session) {


  # DATA --------------------------------------------------------------------
  rugby_data <- reactiveValues()
  rugby_data$Data <- df %>%
    mutate(Season = ifelse(month(Date) < 6,
                           paste0(year(Date) - 1, "/", year(Date)),
                           paste0(year(Date), "/", year(Date) + 1)),
           `Home/Away` = ifelse(Venue == "Away", "A", "H"),
           Result = ifelse(`F` == `A`, "D",
                           ifelse(`F` > `A`, "W", "L")),
           Opposition_club = str_replace_all(Opposition, "\\s\\(?[0-9](st|nd|rd|th)\\)?", ""))

  output$new_data <- renderUI({
    fluidRow(
      box(
        width = 12,
        title = "Add latest game",
        collapsible = T,
        collapsed = T,
        status = "warning",
        solidHeader = F,
        column(
          6,
          wellPanel(
            h4("Fixture"),
            fluidRow(
              column(4, dateInput("date", "Date", value = Sys.Date(), format = "dd MM yyyy")),
              column(4, pickerInput("team", "Team", choices = levels(rugby_data$Data$Team), selected = "2nd")),
              column(4, textInput("opposition", "Opposition"))),
            fluidRow(
              column(4, textInput("competition", "Competition")),
              column(4, pickerInput("stage", "Stage", choices = c("", levels(rugby_data$Data$Stage)))),
              column(4, pickerInput("venue", "Venue", choices = levels(as.factor(rugby_data$Data$Venue)), selected = "Ealing")))
          ),
          actionButton("add_game", "Add new game", icon = icon("save"),
                       style="color: #fff; background-color: #337ab7; border-color: #2e6da4")
        ),
        column(
          6,
          wellPanel(
            h4("Result"),
            fluidRow(
              column(3, numericInput("for", "For", min = 0, max = 99, value = 0)),
              column(3, numericInput("against", "Against", min = 0, max = 99, value = 0)),
              column(3, numericInput("time", "Time", min = 0, max = 80, value = 80)),
              column(3, numericInput("try", "Try", min = 0, max = 9, value = 0))),
            fluidRow(
              column(
                3,
                pickerInput("position", "Position",
                            choices = c("Prop", "Hooker", "Lock", "Flanker", "No. 8",
                                        "Scrum Half", "Fly Half", "Centre", "Wing", "Full Back"),
                            selected = "Lock",
                            multiple = T)),
              column(3, awesomeCheckbox("start", strong("Start?"), value = T)),
              column(3, awesomeCheckbox("motm", strong("MOTM?"), value = F, status = "success")),
              column(3, awesomeCheckbox("yc", strong("YC?"), value = F, status = "warning"))
            ),
            textInput("notes", "Notes")
          )
        )
      )
    )
  })

  ## Table of results
  output$dataTable <- DT::renderDataTable({
    DT = for_display(rugby_data$Data %>%
                       filter((Team == input$team_filter | input$team_filter == "All"),
                              (Season == input$season_filter | input$season_filter == "All"),
                              (Opposition_club %in% input$oppo_filter | is.null(input$oppo_filter))) %>%
                       arrange(desc(Date)) %>%
                       select(-Opposition_club))

    table <- datatable(DT,
                       escape = F,
                       #extensions = 'FixedHeader',
                       options = list(
                         columnDefs = list(list(visible=FALSE, targets=c(6))),
                         pageLength = 10,
                         fixedHeader = TRUE,
                         dom = 'ltp',
                         ordering = F,
                         autoWidth = TRUE
                       ),
                       rownames = F,
                       selection = "none")

    if(input$color_data_by == "Result"){
      table <- table %>%
        formatStyle('Result', target = 'row',
                    backgroundColor = styleEqual(c("W", "L", "D"),
                                                 c("rgb(200,255,200)", "rgb(255,200,200)", "rgb(255,255,200)")))
    } else if(input$color_data_by == "Team"){
      table <- table %>%
        formatStyle('Team', target = 'row',
                    backgroundColor = styleEqual(c("1st", "2nd", "Evergreens", "Exiles"),
                                                 c("rgb(200,255,200)", "rgb(255,200,100)",
                                                   "rgb(200,200,200)", "rgb(250,250,250)")))
    }
    return(table)
  })

  ## Save table to changes.csv
  observeEvent(input$add_game, {
    rugby_data$Data <- rugby_data$Data %>%
      add_row(Date = as.Date(input$date, format = "%Y-%m-%d"),
              Team = input$team,
              Competition = input$competition,
              Stage = input$stage,
              Opposition = input$opposition,
              Venue = input$venue,
              `F` = input$`for`,
              `A` = input$against,
              Position = glue::collapse(input$position, sep = "/"),
              Time = input$time,
              Start = input$start,
              MOTM = input$motm,
              YC = input$yc,
              Try = input$try,
              Notes = input$notes) %>%
      mutate(Season = ifelse(month(Date) < 6,
                             paste0(year(Date) - 1, "/", year(Date)),
                             paste0(year(Date), "/", year(Date) + 1)),
             `Home/Away` = ifelse(Venue == "Away", "A", "H"),
             Result = ifelse(`F` == `A`, "D",
                             ifelse(`F` > `A`, "W", "L")),
             Opposition_club = str_replace_all(Opposition, "\\s\\(?[0-9](st|nd|rd|th)\\)?", ""))

    write_csv(rugby_data$Data, "Rugby_clean.csv")

    showModal(modalDialog(title = "Game saved", em("Rugby_clean.csv"), " overwritten with new data", easyClose = TRUE, size = "s"))
  })


  stats_data <- reactive(
    rugby_data$Data %>%
      filter(Team == input$stats_team | input$stats_team == "All",
             Season == input$stats_season | input$stats_season == "All",
             Opposition_club == input$stats_oppo | input$stats_oppo == "All"))

  # FILTERS -----------------------------------------------------------------

  output$season_filter_input <- renderUI({
    pickerInput("season_filter", "Season filter",
                choices = c("All", unique(rugby_data$Data$Season)),
                selected = "All")
  })

  output$team_filter_input <- renderUI({
    pickerInput("team_filter", "Team filter",
                choices = c("All", as.character(sort(unique(rugby_data$Data$Team)))),
                selected = "All")
  })

  output$oppo_filter_input <- renderUI({
    pickerInput("oppo_filter", "Opposition filter",
                choices = sort(unique(rugby_data$Data$Opposition_club)),
                multiple = T,
                options = list(
                  #style = "btn-primary",
                  title = "Choose a club (e.g. \"Wasps\")",
                  `live-search` = TRUE)
    )
  })

  output$stats_filters <- renderUI({
    column(
      width = 2,
      pickerInput("stats_team", "Team",
                  choices = c("All", as.character(sort(unique(rugby_data$Data$Team)))),
                  selected = "All") %>%
        popify(title = "",
               content = "Select an Ealing team played for, or \"All\" to include games for all teams."),
      pickerInput("stats_season", "Season",
                  choices = c("All", unique(rugby_data$Data$Season)),
                  selected = "All") %>%
        popify(title = "",
               content = "Select a season, or \"All\" to include all games."),
      pickerInput("stats_oppo", "Opposition",
                  choices = c("All", sort(unique(rugby_data$Data$Opposition_club))),
                  selected = "All",
                  options = list(
                    #style = "btn-primary",
                    `actions-box` = TRUE,
                    `live-search` = TRUE)) %>%
        popify(title = "",
               content = "Select from a list of clubs played against, or \"All\" to include all opposition. There is no distinction between different teams from the same club.")
    )
  })




  # CHARTS ------------------------------------------------------------------

  output$plot_cum_time <- renderHighchart(hc_cum_time(rugby_data$Data))
  output$plot_cum_games <- renderHighchart(hc_cum_games(rugby_data$Data))
  output$plot_tries <- renderHighchart(hc_tries(rugby_data$Data))
  output$plot_games_team <- renderHighchart(hc_games_by_team(rugby_data$Data))
  output$plot_tot_games_team <- renderHighchart(hc_tot_games_by_team(rugby_data$Data))
  output$plot_mins_team <- renderHighchart(hc_mins_by_team(rugby_data$Data))
  output$plot_tot_mins_team <- renderHighchart(hc_tot_mins_by_team(rugby_data$Data))
  output$plot_games_season <- renderHighchart(hc_games_by_season(rugby_data$Data))
  output$plot_tot_games_season <- renderHighchart(hc_tot_games_by_season(rugby_data$Data))
  output$plot_games_position <- renderHighchart(hc_games_by_position(rugby_data$Data))
  output$plot_tot_games_position <- renderHighchart(hc_tot_games_by_position(rugby_data$Data))
  output$plot_scores <- renderHighchart(hc_score_map(rugby_data$Data))
  output$table_win_rate <- renderFormattable(dt_win_rate(rugby_data$Data))
  output$table_avg_score_team <- renderFormattable(dt_average_score_team(rugby_data$Data))
  output$table_avg_score_season <- renderFormattable(dt_average_score_season(rugby_data$Data))

  output$plot_games <- renderUI({
    if(input$toggle_by_team){
      fluidRow(
        column(6, highchartOutput("plot_games_season")),
        column(6, highchartOutput("plot_games_position")))
    } else {
      fluidRow(
        column(6, highchartOutput("plot_tot_games_season")),
        column(6, highchartOutput("plot_tot_games_position")))
    }
  })

  # STATS (ValueBoxes) ------------------------------------------------------

  output$game_count <- renderValueBox({
    valueBox(
      paste0(nrow(stats_data()), " (", sum(stats_data()$Start),")"),
      "Games (starts)",
      color = "blue",
      icon = icon("users")
    )
  })

  output$minute_count <- renderValueBox({
    avg_time <- round(sum(stats_data()$Time / nrow(stats_data())))

    valueBox(
      paste0(format(sum(stats_data()$Time), big.mark = ","),
             " (", avg_time, ")"),
      "Minutes (per game)",
      color = "blue",
      icon = icon("clock-o")
    )
  })

  output$try_count <- renderValueBox({
    valueBox(
      sum(stats_data()$Try),
      "Tries",
      color = "green",
      icon = icon("star"))
  })

  output$card_count <- renderValueBox({
    valueBox(
      sum(stats_data()$YC),
      "Yellows",
      color = "yellow",
      icon = icon("square"))
  })

  output$win_rate <- renderValueBox({
    valueBox(stats_data() %>%
               summarise(Games = n(),
                         Wins = sum(Result == "W", na.rm = T)) %>%
               mutate(win_rate = ifelse(Games == 0, "-",
                                        scales::percent(round(Wins/Games, 2)))) %>%
               .$win_rate,
             "Overall",
             color = "blue")
  })

  output$win_rate_home <- renderValueBox({
    valueBox(stats_data() %>%
               filter(`Home/Away` == "H") %>%
               summarise(Games = n(),
                         Wins = sum(Result == "W", na.rm = T)) %>%
               mutate(win_rate = ifelse(Games == 0, "-",
                                        scales::percent(round(Wins/Games, 2)))) %>%
               .$win_rate,
             "Home")
  })

  output$win_rate_away <- renderValueBox({
    valueBox(stats_data() %>%
               filter(`Home/Away` == "A") %>%
               summarise(Games = n(),
                         Wins = sum(Result == "W", na.rm = T)) %>%
               mutate(win_rate = ifelse(Games == 0, "-",
                                        scales::percent(round(Wins/Games, 2)))) %>%
               .$win_rate,
             "Away")
  })

  output$avg_score <- renderValueBox({
    valueBox(stats_data() %>%
               summarise(For = round(mean(`F`, na.rm = T)),
                         Against = round(mean(`A`, na.rm = T))) %>%
               mutate(avg_score = paste(ifelse(is.na(For), " ", For), "-",
                                        ifelse(is.na(Against), " ", Against))) %>%
               .$avg_score,
             "Overall",
             color = "blue")
  })

  output$avg_score_home <- renderValueBox({
    valueBox(stats_data() %>%
               filter(`Home/Away` == "H") %>%
               summarise(For = round(mean(`F`, na.rm = T)),
                         Against = round(mean(`A`, na.rm = T))) %>%
               mutate(avg_score = paste(ifelse(is.na(For), " ", For), "-",
                                        ifelse(is.na(Against), " ", Against))) %>%
               .$avg_score,
             "Home")
  })

  output$avg_score_away <- renderValueBox({
    valueBox(stats_data() %>%
               filter(`Home/Away` == "A") %>%
               summarise(For = round(mean(`F`, na.rm = T)),
                         Against = round(mean(`A`, na.rm = T))) %>%
               mutate(avg_score = paste(ifelse(is.na(For), " ", For), "-",
                                        ifelse(is.na(Against), " ", Against))) %>%
               .$avg_score,
             "Away")
  })
}

