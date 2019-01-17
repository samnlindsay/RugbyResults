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
library(shinyBS)
library(stringr)
library(shinycssloaders)
library(highcharter)
library(formattable)
source("charts.R")

ui <- dashboardPage(skin = "green",
                    title = "Ealing Rugby Men's: Sam Lindsay",
                    dashboardHeader(title = HTML("<div align='left'><a href='https://ealingrugby.co.uk/?page_id=12100'><img src='Trailfinders_rfc_logo.png' height='40px'></a> Ealing Rugby Men's: <b>Sam Lindsay</b></div>"),
                                    titleWidth = '420'),
                    dashboardSidebar(
                      width = 150,
                      sidebarMenu(
                        menuItem("Game data", tabName = "data", icon = icon("list-ul")),
                        menuItem("Stats",tabName = "stats", icon = icon("bar-chart-o")),
                        menuItem("Fixtures", icon = icon("calendar"),
                                 menuSubItem("1st", href = "https://ealingrugby.co.uk/?page_id=17590", icon = icon("external-link"), newtab = T),
                                 menuSubItem("2nd", href = "https://ealingrugby.co.uk/?page_id=17589", icon = icon("external-link"), newtab = T),
                                 menuSubItem("Exiles", href = "https://ealingrugby.co.uk/?page_id=17591", icon = icon("external-link"), newtab = T),
                                 menuSubItem("Evergreens", href = "https://ealingrugby.co.uk/?page_id=17592", icon = icon("external-link"), newtab = T))
                      )
                    ),
                    dashboardBody(
                      tags$head(tags$link(rel = "icon", type = "image/png", href = "Trailfinders_rfc_logo.png")),
                      useShinyjs(),
                      tags$style(type="text/css",
                                 ".shiny-output-error { visibility: hidden; }",
                                 ".shiny-output-error:before { visibility: hidden; }"),
                      tabItems(
                        tabItem(
                          tabName = "data",
                          uiOutput("new_data"),
                          fluidRow(
                            box(
                              width = 12,
                              title = "Game history",
                              solidHeader = T,
                              status = "success",
                              fluidRow(
                                column(3, uiOutput("season_filter_input") %>%
                                         popify(title = "", placement = "top",
                                                content = "Select a specific season to view only games that year.")),
                                column(3, uiOutput("team_filter_input") %>%
                                         popify(title = "", placement = "top",
                                                content = "Select an Ealing team to view only games played for that team.")),
                                column(4, uiOutput("oppo_filter_input") %>%
                                         popify(title = "", placement = "top",
                                                content = "Select an opposition club to view only games played against that club (all squads).")),
                                column(2, radioGroupButtons("color_data_by", "Colour rows by...",
                                                            choices = c("Result", "Team"),
                                                            checkIcon = list(
                                                              yes = tags$i(class = "fa fa-check-square",
                                                                           style = "color: steelblue"),
                                                              no = tags$i(class = "fa fa-square-o",
                                                                          style = "color: steelblue"))
                                ) %>%
                                  popify(title = "", placement= "top", content = "Color rows by result <br> (W/L = green/red) <br> or team played for <br> (1st/2nd = green/orange)"))
                              ),
                              tags$hr(),
                              column(12, DT::dataTableOutput("dataTable") %>% withSpinner())
                            )
                          )
                        ),
                        tabItem(
                          tabName = "stats",
                          fluidRow(
                            uiOutput("stats_filters"),
                            tabBox(
                              title = "Summary stats",
                              side = "right",
                              width = 10,
                              tabPanel(
                                title = "Quick stats",
                                fluidRow(valueBoxOutput("game_count", width = 12)),
                                fluidRow(valueBoxOutput("minute_count", width = 12)),
                                fluidRow(valueBoxOutput("try_count", width = 6),
                                         valueBoxOutput("card_count", width = 6))
                              ),
                              tabPanel(
                                title = "Win percentage",
                                status = "success",
                                tags$div(fluidRow(valueBoxOutput("win_rate", width = 12)),
                                fluidRow(valueBoxOutput("win_rate_home", width = 12)),
                                fluidRow(valueBoxOutput("win_rate_away", width = 12))
                              ) %>%
                                popify(title = "", content = "Overall win rate (top) and separately at home and away.",
                                       placement = "top", trigger = "hover")),
                              tabPanel(
                                title = "Average score",
                                status = "success",
                                tags$div(fluidRow(valueBoxOutput("avg_score", width = 12)),
                                fluidRow(valueBoxOutput("avg_score_home", width = 12)),
                                fluidRow(valueBoxOutput("avg_score_away", width = 12))
                              ) %>%
                                popify(title = "", placement = "top", trigger = "hover",
                                       content = "Average points for and against in all games (top), home games and away games. Ealing score is shown first.")))
                          ),
                          fluidRow(
                            box(
                              title = "Scores",
                              width = 6,
                              collapsible = T,
                              collapsed = T,
                              solidHeader = T,
                              status = "success",
                              highchartOutput("plot_scores")
                            ),
                            box(
                              title = "Cumulative game time",
                              width = 6,
                              collapsible = T,
                              collapsed = T,
                              solidHeader = T,
                              status = "success",
                              radioGroupButtons("cum_games_or_mins", label = NULL, choices = c("Games", "Minutes"), justified = TRUE),
                              conditionalPanel("input.cum_games_or_mins == 'Games'", highchartOutput("plot_cum_games")),
                              conditionalPanel("input.cum_games_or_mins == 'Minutes'", highchartOutput("plot_cum_time"))
                            )
                          ),
                          fluidRow(
                            box(
                              title = "Game count",
                              width = 12,
                              collapsible = T,
                              collapsed = T,
                              solidHeader = T,
                              status = "success",
                              switchInput("toggle_by_team", "Break down by team", value = F, labelWidth = "150px", onStatus = "warning"),
                              br(),
                              uiOutput("plot_games")
                            )
                          )
                        )
                      ))
)
