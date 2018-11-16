library(shiny)
library(shinydashboard)
library(DT)
library(dplyr)
library(readr)
library(lubridate)
library(data.table)
library(shinyWidgets)
library(shinyjs)

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
      ),
    br(),
    br(),
    uiOutput("season_filter_input"),
    uiOutput("team_filter_input")
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
                         column(12, DT::dataTableOutput("dataTable"))
                         ))
            ),
      tabItem(tabName = "analysis",
            "Some plots")
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
                           no = icon("remove", lib = "glyphicon")),
                         direction = "vertical")
  })

  output$team_filter_input <- renderUI({
    checkboxGroupButtons("team_filter",
                         "Team Filter",
                         choices = levels(df$Team),
                         selected = levels(df$Team),
                         justified = T,
                         checkIcon = list(
                           yes = icon("ok", lib = "glyphicon"),
                           no = icon("remove", lib = "glyphicon")),
                         direction = "vertical")
  })

  output$team_filter_input <- renderUI({
    checkboxGroupButtons("team_filter",
                         "Team Filter",
                         choices = levels(df$Team),
                         selected = levels(df$Team),
                         justified = T,
                         checkIcon = list(
                           yes = icon("ok", lib = "glyphicon"),
                           no = icon("remove", lib = "glyphicon")),
                         direction = "vertical")
  })

  ## Table of results
  output$dataTable <- DT::renderDataTable({
    DT = for_display(rugby_data$Data %>%
                       filter(Season %in% input$season_filter,
                              Team %in% input$team_filter) %>%
                       arrange(desc(Date)))

    datatable(DT,
              escape = F,
              extensions = 'FixedHeader',
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

}

# Run the application
shinyApp(ui = ui, server = server)

