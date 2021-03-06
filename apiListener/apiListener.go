package main

import (
	"database/sql"
	"fmt"
	"net"
	"net/http"
	"net/http/fcgi"
	"strings"

	"../goconf"
	"github.com/gidoBOSSftw5731/log"
	"github.com/jinzhu/configor"
)

type newFCGI struct{}

var (
	config goconf.Config
	db     *sql.DB
)

func main() {
	//Boilerplate config
	configor.Load(&config, "config.yml")
	log.SetCallDepth(4)

	//init the DB
	var err error
	db, err = goconf.MkDB(&config)
	if err != nil {
		log.Fatalln(err)
	}
	//ping and fatal on error (sometimes catches bugs)
	if db.Ping() != nil {
		log.Fatalln(db.Ping())
	}

	log.Traceln("Listening")
	//begin fcgi listener, we use fcgi so we can have a loadbalancer and a cache upstream
	listener, err := net.Listen("tcp", "127.0.0.1:9001")
	if err != nil {
		log.Fatalln(err)
	}
	var h newFCGI
	fcgi.Serve(listener, h)
}

func (h newFCGI) ServeHTTP(resp http.ResponseWriter, req *http.Request) {
	urlSplit := strings.Split(req.URL.Path, "/")

	if len(urlSplit) < 2 {
		ErrorHandler(resp, req, 400,
			"This is the API, please make a request (in place of docs, DM GidoBOSSftw5731#6422 on discord")
		return
	}

	switch urlSplit[1] {
	case "stateinfo":
		if len(urlSplit) >= 2 {
			ErrorHandler(resp, req, 400, "Specify a state or county there bud")
			return
		}
		if len(urlSplit) == 3 {
			//indentify by state
		} else if len(urlSplit) == 4 {
			//identify by county
		} else {
			ErrorHandler(resp, req, 400, "Too many arguments")
			return
		}
	case "liststates":
		if len(urlSplit) >= 1 {
			ErrorHandler(resp, req, 400, "Ya did it wrong (this is a logically impossible error)")
			return
		}
		if len(urlSplit) == 2 {
			//list states
		} else if len(urlSplit) == 3 {
			//list counties
		} else {
			ErrorHandler(resp, req, 400, "Too many arguments")
			return
		}
	default:
		ErrorHandler(resp, req, 400, "Bad request")
		return
	}
}

//ErrorHandler is a function to handle HTTP errors
func ErrorHandler(resp http.ResponseWriter, req *http.Request, status int, alert string) {
	resp.WriteHeader(status)
	log.Errorf("HTTP error: %v, witty message: %v", status, alert)
	fmt.Fprintf(resp, "You have found an error! This error is of type %v. Built in alert: \n'%v',\n Would you like a <a href='https://http.cat/%v'>cat</a> or a <a href='https://httpstatusdogs.com/%v'>dog?</a>",
		status, alert, status, status)
}
