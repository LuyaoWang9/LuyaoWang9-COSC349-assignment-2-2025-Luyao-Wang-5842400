#!/bin/bash
KEY_PATH="notebook.pem"

echo "🏥 Application Health Check"

# Backend health
echo "🔧 Backend:"
ssh -i $KEY_PATH ec2-user@ec2-54-87-53-238.compute-1.amazonaws.com "curl -s http://localhost:5054/health | python3 -m json.tool"

# Frontend health  
echo "🌐 Frontend:"
ssh -i $KEY_PATH ec2-user@ec2-98-89-23-110.compute-1.amazonaws.com "curl -s -o /dev/null -w 'HTTP Status: %{http_code}\n' http://localhost"

echo "✅ All systems operational!"