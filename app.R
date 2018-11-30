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
source("charts.R")

for_display <- function(df){
  df %>%
    mutate(Date = format(Date, "%d %b %Y"),
           Start = ifelse(Start, "<i class='fa fa-check' style='color:green' align='center'></i>", ""),
           MOTM = ifelse(MOTM, "<i class='fa fa-trophy' style='color:green' align='center'></i>", ""),
           YC = ifelse(YC, "<i class='fa fa-square' style='color:#ffcc00' align='center''></i>", ""),
           Try = ifelse(Try > 0, strrep("<i class='fa fa-star' style='color:green' align='center'></i>", Try), "")) %>%
    select(-Season, -Result, -`Home/Away`)
}

df <- read_csv("Rugby_clean.csv", col_types = "cDccccccciicilllic") %>%
  mutate_at(c("Team", "Stage", "Home/Away", "Result"), as.factor)

# Define UI for application that draws a histogram
ui <- dashboardPage(
  dashboardHeader(title = "Rugby Results"),
  dashboardSidebar(
    sidebarMenu(
      menuItem("Data", tabName = "data", icon = icon("table")),
      menuItem("Analysis", tabName = "analysis", icon = icon("bar-chart-o"))
      )
  ),
  dashboardBody(
    useShinyjs(),
    fluidRow(
      valueBoxOutput("match_count", width = 3),
      valueBoxOutput("minute_count", width = 3),
      valueBoxOutput("try_count", width = 3),
      valueBoxOutput("card_count", width = 3)),
    uiOutput("new_data"),
    tabItems(
      tabItem(tabName = "data",
            fluidRow(box(width = 12,
                         title = "Match History",
                         collapsible = TRUE,
                         status = "primary",
                         #solidHeader = TRUE,
                         fluidRow(
                           column(6, uiOutput("season_filter_input")),
                           column(6, uiOutput("team_filter_input"))
                           ),
                         column(12, DT::dataTableOutput("dataTable"))
                         ))
            ),
      tabItem(tabName = "analysis",
            fluidRow(box(
              title = "Scores",
              width = 12,
              collapsible = T,
              fluidRow(
                column(6, highchartOutput("plot_scores")),
                column(3, highchartOutput("plot_games_team"))
                )
              )),
            fluidRow(box(title = "Cumulative games/minutes played",
                width = 12,
                collapsible = T,
                fluidRow(
                  column(6, radioGroupButtons("cum_games_or_mins", label = NULL,
                              choices = c("Games", "Minutes"), justified = TRUE),
                         conditionalPanel("input.cum_games_or_mins == 'Games'",
                           highchartOutput("plot_cum_games")),
                         conditionalPanel("input.cum_games_or_mins == 'Minutes'",
                           highchartOutput("plot_cum_time"))),
                  column(6, box(width = 12,
                                formattableOutput("table_win_rate")),
                         box(width = 12,
                             formattableOutput("table_avg_score_team"),
                             formattableOutput("table_avg_score_season")))
                )
                )),
            fluidRow(box(
              title = "Game count",
              width = 12,
              collapsible = T,
              switchInput("toggle_by_team", "Break down by team",
                          value = T, labelWidth = "150px", onStatus = "warning"),
              br(),
              uiOutput("plot_games")
              ))
      )
    )
  )
)

# Define server logic required to draw a histogram
server <- function(input, output) {

  rugby_data <- reactiveValues()
  rugby_data$Data <- df %>%
    mutate(Season = ifelse(month(Date) < 6,
                           paste0(year(Date) - 1, "/", year(Date)),
                           paste0(year(Date), "/", year(Date) + 1)),
           `Home/Away` = ifelse(Venue == "Away", "A", "H"),
           Result = ifelse(`F` == `A`, "D",
                           ifelse(`F` > `A`, "W", "L")))

  output$match_count <- renderValueBox({
    valueBox(
      paste0(nrow(rugby_data$Data), " (", sum(rugby_data$Data$Start),")"),
      "Matches played (started)",
      color = "blue",
      icon = icon("users")
    )
  })

  output$minute_count <- renderValueBox({
    valueBox(
      format(sum(rugby_data$Data$Time), big.mark = ","),
      "Minutes played",
      color = "blue",
      icon = icon("clock-o")
    )
  })

  output$try_count <- renderValueBox({
    valueBox(
      sum(rugby_data$Data$Try),
      "Tries",
      color = "green",
      icon = icon("star"))
  })

  output$card_count <- renderValueBox({
    valueBox(
      sum(rugby_data$Data$YC),
      "Yellow cards",
      color = "yellow",
      icon = icon("square"))
  })

  output$new_data <- renderUI({
    fluidRow(
      box(width = 12,
          title = "Add new match",
          collapsible = T,
          collapsed = T,
          status = "primary",
          column(6, wellPanel(
            h4("Fixture"),
            fluidRow(
              column(4, airDatepickerInput("date", "Date",
                                           value = Sys.Date())),
              column(4, pickerInput("team", "Team",
                                    choices = levels(rugby_data$Data$Team),
                                    selected = "2nd")),
              column(4, textInput("opposition", "Opposition"))),
            fluidRow(
              column(4, textInput("competition", "Competition")),
              column(4, pickerInput("stage", "Stage",
                                    choices = c("", levels(rugby_data$Data$Stage)))),
              column(4, pickerInput("venue", "Venue",
                                    choices = levels(as.factor(rugby_data$Data$Venue)), selected = "Ealing")))
          ),
          actionButton("add_match", "Add new match", icon = icon("save"),
                       style="color: #fff; background-color: #337ab7; border-color: #2e6da4")),
          column(6, wellPanel(
            h4("Result"),
            fluidRow(
              column(3, numericInput("for", "For", min = 0, max = 99, value = 0)),
              column(3, numericInput("against", "Against", min = 0, max = 99, value = 0)),
              column(3, numericInput("time", "Time", min = 0, max = 80, value = 80)),
              column(3, numericInput("try", "Try", min = 0, max = 9, value = 0))),
            fluidRow(
              column(3, pickerInput("position", "Position",
                                    choices = c("Prop", "Hooker", "Lock", "Flanker", "No. 8",
                                                "Scrum Half", "Fly Half", "Centre", "Wing", "Full Back"),
                                    selected = "Lock",
                                    multiple = T)),
              column(3, awesomeCheckbox("start", strong("Start?"), value = T)),
              column(3, awesomeCheckbox("motm", strong("MOTM?"), value = F, status = "success")),
              column(3, awesomeCheckbox("yc", strong("YC?"), value = F, status = "warning"))
            ),
            textInput("notes", "Notes")
          ))
      ))
  })

  output$season_filter_input <- renderUI({
    checkboxGroupButtons("season_filter",
                         "Season Filter",
                         choices = unique(rugby_data$Data$Season),
                         selected = unique(rugby_data$Data$Season),
                         justified = T,
                         checkIcon = list(
                           yes = icon("ok", lib = "glyphicon"),
                           no = icon("remove", lib = "glyphicon")))
  })

  output$team_filter_input <- renderUI({
    checkboxGroupButtons("team_filter",
                         "Team Filter",
                         choices = levels(df$Team),
                         selected = levels(df$Team),
                         justified = T,
                         checkIcon = list(
                           yes = icon("ok", lib = "glyphicon"),
                           no = icon("remove", lib = "glyphicon")))
  })

  ## Table of results
  output$dataTable <- DT::renderDataTable({
    DT = for_display(rugby_data$Data %>%
                       filter(Season %in% input$season_filter,
                              Team %in% input$team_filter) %>%
                       arrange(desc(Date)))

    datatable(DT,
              escape = F,
              #extensions = 'FixedHeader',
              options = list(
                pageLength = 10,
                fixedHeader = TRUE,
                dom = 'ltp',
                ordering = F,
                autoWidth = TRUE
              ),
              rownames = F,
              selection = "none")
  })

  ## Save table to changes.csv
  observeEvent(input$add_match, {
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
                             ifelse(`F` > `A`, "W", "L")))

    write_csv(rugby_data$Data, "Rugby_clean.csv")

    showModal(modalDialog(title = "Game saved", em("Rugby_clean.csv"), " overwritten with new data", easyClose = TRUE, size = "s"))
  })

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

}

# Run the application
shinyApp(ui = ui, server = server)

