# Quakebots Frequency Domain Decomposition Docker Image

docker build -t wiserobotics.azurecr.io/fdd_docker:1.2 .

# Run locale
docker run -p 5000:5000 wiserobotics.azurecr.io/fdd_docker:1.2

# Run remoto
docker run -d -p 5000:5000 -e "CAPI=http://192.168.1.12:82" --restart unless-stopped wiserobotics.azurecr.io/fdd_docker:1.2

export CAPI=https://www.quake.cloud


main.py

@app.route('/FDD', methods=['GET','POST'])
Compute the FDD analysis 

REQUEST:

{"device_id": [1042,1043,5000,6000],
 "time_min": "2019-08-10T07:48:00.000Z",
 "time_max": "2019-08-10T07:58:00.000Z",
 "axis": ["x"],
"filtering":"lowpass",
"fmin":5,
"fmax":6,
"order":1,
 "return_acc": 1}

RESPONSE:

{
“success": “True",
“error": {
         “code":-1,
         “message": "no response by: 5000,6000",
   },
“result": {
        “Frq":[
7.75
],
“S": [
           […
           ],
           […
           ],
           […
           ],
           […
           ]
  ],
“U": [
           […
           ],
           […
           ],
           […
           ],
           […
           ]
  ],
“f": […
],
“peaks": [
8]
}
}

Error code:

0: application completed 
-1: "no response by: .."
-2: "no data available for the FDD application. Not enough"
-3: "no data available for all devices"
-4: "well-formed but invalid JSON:"
-5: "poorly-formed text, not JSON:"

“FRQ": ESTIMATED MODAL FREQUENCIES(HZ).
“S": MATRIX OF SINGULAR VALUES.  SIZE: (SIZE DEVIDEID*SIZE AXIS)X(SIZE PSD OF SINGLE AXIS)-> FIRST SINGULAR VALUES CURVE IS S[0]
“U":MATRIX OF MODEL SHAPES. SIZE: THE SAME SIZE OF S MATRIX.
“F": FREQUENCY AXIS(HZ).
“PEAKS": MODAL FREQUENCIES POSITION IN SAMPLES.
-----------------------------------------------------
@app.route('/integration_ids', methods=['GET','POST'])
Comupute  chunk integration for displacement and velocity

REQUEST:

{"ids":2000000,
"filtering":"bandpass",
  "fmin":5,
  "fmax":10,
  "order":4
  }

RESPONSE:

{ 
 “success": “True",
 “error": {
         “code":0,
   }
 “result": {  “velocity”:{“x":[..],
“y":[..],
“z":[..]},
                    “displacement”:{“x":[..],
“y":[..],
“z":[..]},

                   “metrics":{“max_displacement”:{“x": ..,
“y": ..,
“z": ..},
                                      “max_velocity”:{“x": ..,
“y": ..,
“z": ..},
                “API_info”:[……..]
             }
}

Error code:

0: application completed
-1: "error in getDataByKey"
-4: "well-formed but invalid JSON:"
-5: "poorly-formed text, not JSON:"
---------------------------------------------------------
@app.route('/displacement_device', methods=['GET','POST'])

REQUEST:

{'device_id': 1042,
 'time_min': '2019-08-10T07:48:00.000Z',
 'time_max': '2019-08-10T07:58:00.000Z',
 'timestep':1}

RESPONSE:

{
“success": “True",
“error":{“code": 0
},
“result": {“velocity":{“x":[..],
“y":[..],
“z":[..]},
                 “displacement":{“x":[..],
“y":[..],
“z":[..]},
                   “acceleration":{“x":[..],
“y":[..],
“z":[..]}
          }
}

Error code:

0: application completed
-1: "error in GetTimedSamplesByKey"
-4: "well-formed but invalid JSON:"
-5: "poorly-formed text, not JSON:"
------------------------------------------
@app.route('/PSD', methods=['GET','POST'])
Compute the PSD of the device channels for a given period of time

REQUEST:

{"device_id": 1042,
"time_min":"2019-08-10T07:48:00.000Z",
"time_max":"2019-08-10T07:50:00.000Z"
}

RESPONSE:

{
"success": true
“error":{“code": 0
},
“result": {“freq":[..],
                 “psd_x":[..],
                 “psd_y":[..],
                 “psd_z":[..],
                  “vel_z":[..],
  “acceleration”:{“x":[..],
“y":[..],
“z":[..]}
 }
}

Error code:

0: application completed
-1: "Extraction error"
-4: "well-formed but invalid JSON:"
-5: "poorly-formed text, not JSON:"

FREQ IS THE FREQUENCY AXIS (HZ). ACCELERATION AS IN INPUT (MILLIG). 
