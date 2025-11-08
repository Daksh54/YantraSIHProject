import React, { useState } from "react";
import * as THREE from "three";
import "./index.css";
import { Button } from "./components/ui/button.jsx";
import { Card, CardContent } from "./components/ui/card.jsx";
import { Input } from "./components/ui/input.jsx";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "./components/ui/select.jsx";
import {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
} from "./components/ui/tabs.jsx";
import { Calendar, TimePicker } from "./components/ui/calendar.jsx";
import { Download, FileText } from "lucide-react";

export default function App() {
  const [location, setLocation] = useState("Delhi");
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [yantraType, setYantraType] = useState("Samrat Yantra");
  const [scale, setScale] = useState("3.0 m");
  const [date, setDate] = useState(new Date("2024-04-24"));
  const [time, setTime] = useState("12:00");

  return (
    <div className="min-h-screen bg-[#345a70] flex flex-col items-center p-6">
      {/* Header */}
      <div className="w-full max-w-6xl bg-[#345a70] text-[#debc81] rounded-t-2xl p-4 flex justify-between items-center">
        <h1 className="text-2xl text-white font-bold">Build Your Yantra</h1>
        <p className="italic text-sm text-white">
          Ancient Indian astronomy reimaginated with modern software
        </p>
      </div>

      <div className="w-full max-w-6xl bg-[#debc81] border border-[#d8c5a1] rounded-b-2xl p-6 grid grid-cols-12 gap-6">
        {/* Left Panel */}
        <div className="col-span-3 space-y-4">
          <div>
            <label className="text-sm font-semibold">Location</label>
            <Input
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="mt-1"
            />
          </div>

          <div>
            <label className="text-sm font-semibold">Latitude</label>
            <Input
              type="number"
              value={latitude}
              onChange={(e) => setLatitude(e.target.value)}
              className="mt-1"
              placeholder="Enter latitude"
            />
          </div>

          <div>
            <label className="text-sm font-semibold">Longitude</label>
            <Input
              type="number"
              value={longitude}
              onChange={(e) => setLongitude(e.target.value)}
              className="mt-1"
              placeholder="Enter longitude"
            />
          </div>

          <div>
            <label className="text-sm font-semibold">Yantra Type</label>
            <Select value={yantraType} onValueChange={setYantraType}>
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="Select Yantra" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Samrat Yantra">Samrat Yantra</SelectItem>
                <SelectItem value="Jai Prakash Yantra">
                  Jai Prakash Yantra
                </SelectItem>
                <SelectItem value="Other Yantra">Other Yantra</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="text-sm font-semibold">Scale</label>
            <Input
              value={scale}
              onChange={(e) => setScale(e.target.value)}
              className="mt-1"
            />
          </div>

          <div>
            <label className="text-sm font-semibold">Date</label>
            <Calendar
              selected={date}
              onSelect={setDate}
              className="mt-2 border rounded-md"
            />
          </div>

          {/* Conditional Time Input */}
          {yantraType !== "Samrat Yantra" && (
            <div>
              <label className="text-sm font-semibold">Time</label>
              <Input
                type="time"
                value={time}
                onChange={(e) => setTime(e.target.value)}
                className="mt-2 border rounded-md"
              />
            </div>
          )}

          <Button className="w-full bg-[#264f73] text-white margin-top-4 mt-4">
            Generate Yantra
          </Button>
        </div>

        {/* Center Panel */}
        <div className="col-span-6">
          <Tabs defaultValue="blueprint">
            <TabsList className="bg-[#345a70] text-[#debc81] mb-4">
              <TabsTrigger value="blueprint">Blueprint View</TabsTrigger>
              <TabsTrigger value="simulation">3D Simulation</TabsTrigger>
              <TabsTrigger value="dimensions">Dimension Table</TabsTrigger>
            </TabsList>

            <TabsContent value="blueprint" className="p-6">
              <Card>
                <CardContent className="flex justify-center items-center p-6">
                  {/* SVG Blueprint */}
                  <svg viewBox="0 0 400 250" className="max-h-72">
                    <circle
                      cx="200"
                      cy="200"
                      r="120"
                      stroke="#000"
                      fill="none"
                    />
                    {[...Array(12)].map((_, i) => {
                      const angle = (i - 6) * 15 * (Math.PI / 180);
                      const x = 200 + 120 * Math.cos(angle);
                      const y = 200 + 120 * Math.sin(angle);
                      return (
                        <line
                          key={i}
                          x1="200"
                          y1="200"
                          x2={x}
                          y2={y}
                          stroke="#000"
                        />
                      );
                    })}
                    <polygon
                      points="200,80 200,200 240,200"
                      fill="#d8a860"
                      stroke="#000"
                    />
                    <line
                      x1="200"
                      y1="200"
                      x2="240"
                      y2="120"
                      stroke="#000"
                      strokeDasharray="4"
                    />
                    <text x="245" y="115" fontSize="12" fill="#000">
                      28.6°
                    </text>
                  </svg>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="simulation" className="p-6">
              <Card>
                <CardContent className="p-6 text-center">
                  3D Simulation Placeholder
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="dimensions" className="p-6">
              <Card>
                <CardContent className="p-6 text-center">
                  Dimension Table Placeholder
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        {/* Right Panel */}
        <div className="col-span-3 space-y-4">
          <Card>
            <CardContent className="p-4 text-sm">
              <h2 className="font-semibold mb-1">Historical Note</h2>
              <p>
                The Samrat Yantra in Jaipur is 27 m tall and accurate to 2
                seconds.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-sm">
              <h2 className="font-semibold mb-1">Compare with Ujjain</h2>
              <p>Tilt: if Yantra were built in Ujjain.</p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-sm">
              <h2 className="font-semibold mb-1">Fun Fact</h2>
              <p>
                The word "yantra" means "instrument" or machine in Sanskrit.
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Bottom Buttons */}
        <div className="col-span-12 bg-[#debc81] flex justify-between mt-2">
          <div className="flex gap-4">
            <Button variant="outline col-span-2 border-black 2px-4">
              <Download className="mr-2 h-4 w-4" />
              Download Blueprint (PNG)
            </Button>
            <Button variant="outline">
              <Download className="mr-2 h-4 w-4" />
              Download CAD (DXF/STEP)
            </Button>
            <Button variant="outline">
              <Download className="mr-2 h-4 w-4" />
              Download Data (JSON/CSV)
            </Button>
          </div>
          <Button variant="outline">
            <FileText className="mr-2 h-4 w-4" />
            Export Report
          </Button>
        </div>
      </div>
    </div>
  );
}
