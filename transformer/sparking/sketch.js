function setup() {
  createCanvas(800, 600);
}

function draw() {
  background(255);
  noLoop();
  kandinskyPainting();
}

function kandinskyPainting() {
  for (let i = 0; i < 50; i++) {
    push();
    translate(random(width), random(height));
    rotate(random(TWO_PI));
    scale(random(0.5, 2));
    kandinskyElement();
    pop();
  }
}

function kandinskyElement() {
  const shape = int(random(3));
  const fillColor = color(random(255), random(255), random(255));
  const strokeColor = color(random(255), random(255), random(255));
  const strokeWidth = random(1, 5);

  fill(fillColor);
  stroke(strokeColor);
  strokeWeight(strokeWidth);

  if (shape === 0) {
    ellipse(0, 0, random(20, 100), random(20, 100));
  } else if (shape === 1) {
    rect(0, 0, random(20, 100), random(20, 100));
  } else {
    beginShape();
    for (let i = 0; i < 5; i++) {
      vertex(random(-50, 50), random(-50, 50));
    }
    endShape(CLOSE);
  }
}

